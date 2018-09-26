#!/usr/bin/env python
# coding: utf-8
import sys, json, re
import collections as cl
import codecs
from os import mkdir
from os.path import join, dirname, abspath, exists
from twitter import Twitter, OAuth
from watson_developer_cloud import PersonalityInsightsV3
from flask import Flask, render_template, redirect, request
import config

# Flask初期設定
app = Flask(__name__)

# Twitter API 初期設定
CK = config.get_consumer_key()
CS = config.get_consumer_secret()
AT = config.get_access_token()
AS = config.get_access_secret()
twitter = Twitter(auth=OAuth(AT, AS, CK, CS))

# Watson Personality Insights API 初期設定
UN = config.get_username()
PS = config.get_password()
personality_insights = PersonalityInsightsV3(version='2017-10-13', username=UN, password=PS)

# jsonファイル格納場所
json_folder = join(dirname(abspath('__file__')), 'tmp/')
if not exists(json_folder):
    mkdir(json_folder)

# jsonファイル名を返す
def get_file_name(type, user_name):
    if type == 'tw':
        return 'tweets-' + user_name + '.json'
    elif type == 'an':
        return 'analyzed-' + user_name + 'json'
    else:
        try:
            raise ValueError("ファイル形式は tw/an で指定してください")
        except ValueError as e:
            print(e)

# APIからツイートを取ってくる
def get_user_tweets(screen_name):
    number_of_tweets = 0
    count = 200
    max_id = ''
    tweets = []
    a_timeline = twitter.statuses.user_timeline(
        screen_name=screen_name,
        count=count,
        include_rts='false',
        tweet_mode='extended'
    )
    # 取得件数500
    while number_of_tweets <= 500:
        for tweet in a_timeline:
            number_of_tweets += 1
            tweets.append(tweet['full_text'])
            max_id = tweet['id']
        # 取得件数より指定ユーザーのツイートが少ない場合
        if tweets[-1] == tweets[-2]:
            del tweets[-1]
            break
        a_timeline = twitter.statuses.user_timeline(
            screen_name=screen_name,
            count=count,
            max_id=max_id,
            include_rts='false',
            tweet_mode='extended'
        )
    return tweets

# 余計な文字を省く・実体参照を文字に戻す
def get_shaped_tweets(tweets_list):
    shaped_tweets = []
    rm_replie = re.compile(r'@([A-Za-z0-9_]+)')
    rm_url = re.compile(r'https?://t.co/([A-Za-z0-9_]+)')
    rm_hashtag = re.compile(r'#(\w+)')
    for tweet in tweets_list:
        shape = rm_replie.sub('', tweet)
        shape = rm_url.sub('', shape)
        shape = rm_hashtag.sub('', shape)
        shape = shape.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('\n', ' ')
        shaped_tweets.append(shape)
    return shaped_tweets

# P.I.に突っ込む体裁を整えてjson形式"tweets.json"に
def tweets_conv_json(tweets_list, user_name):
    tweets_json = {}
    tweets_json['contentItems'] = []
    for tweet in tweets_list:
        data = cl.OrderedDict()
        data['content'] = tweet
        data['contenttype'] = 'text/plain'
        data['language'] = 'ja'
        tweets_json['contentItems'].append(data)
    with codecs.open(join(json_folder, get_file_name('tw', user_name)), 'w', 'utf-8') as fw:
        json.dump(tweets_json, fw, indent=4 ,ensure_ascii=False)
    print(get_file_name('tw', user) + 'が生成されました')

# 生成したtweets.jsonをもとにWatsonAPI呼び出し
def get_insights_analytics(user_name):
    with open(join(json_folder, get_file_name('tw', user_name)), encoding='utf-8_sig') as tweets_json:
        profile = personality_insights.profile(
            tweets_json.read(),
            content_type='application/json',
            raw_scores=True,
            consumption_preferences=True
        )
        with open(join(json_folder, get_file_name('an', user)), 'w') as fw:
            json.dump(profile, fw, indent=2)
        print(get_file_name('an', user_name) + 'が生成されました')

# big5のpercentileだけ抽出
def get_big5(user_name):
    with open(join(json_folder, get_file_name('an', user_name)), 'r') as analyzed_json:
        json_data = json.load(analyzed_json)
        big5 = {}
        for data in json_data['personality']:
            big5[data['name']] = data['percentile']
    return big5

# big5の差を取り出す
def get_big5_diff(data, users_list):
    diffs = {}
    for status in data[users_list[0]].keys():
        diffs[status] = abs(data[users_list[0]][status] - data[users_list[1]][status])
    return diffs

# big5の差をパーセンテージに変換
def get_diff_percent(data):
    diff_percents = {}
    for status in data.keys():
        diff_percents[status] = round(100 - data[status] * 100)
    return diff_percents

# big5の差の平均値を出す
def get_diff_avg(data):
    sum = 0
    for diff in data.values():
        sum += diff
    diff_avg = round(sum / len(data))
    return diff_avg

# メイン処理
@app.route('/')
def show_toppage():
    return render_template('index.html')

@app.route('/result', methods=['GET', 'POST'])
def show_result():
    # ユーザー定義
    users = []
    user_name = request.form['user_name']
    target_name = request.form['target_name']
    if not user_name:
        return redirect('/')

    users.append(user_name)
    users.append(target_name)
    print(users)

    #メイン処理
    big5 = {}
    for user in users:
        if exists(join(json_folder, get_file_name('tw', user))) == False:
            tweets = get_user_tweets(user)
            tweets = get_shaped_tweets(tweets)
            tweets_conv_json(tweets, user)
        else:
            print(get_file_name('tw', user) + 'が存在します。既存のファイルで処理を続行します。')

        if exists(join(json_folder, get_file_name('an', user))) == False:
            get_insights_analytics(user)
        else:
            print(get_file_name('an', user) + 'が存在します。既存のファイルで処理を続行します。')
        big5[user] = get_big5(user)

    big5_diff = get_big5_diff(big5, users)
    big5_diff_percent= get_diff_percent(big5_diff)
    big5_diff_avg = get_diff_avg(big5_diff_percent)

    # グラフにデータを渡す
    labels = []
    values = []
    for label, value in big5_diff_percent.items():
        labels.append(label)
        values.append(value)

    print(labels)
    print(values)
    return render_template('result.html', values=values, labels=labels, avg=big5_diff_avg)

if __name__ == "__main__":
    app.run(debug=True)
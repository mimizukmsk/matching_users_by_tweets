from os import environ

# Twitter API
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_TOKEN = environ['ACCESS_TOKEN']
ACCESS_SECRET = environ['ACCESS_SECRET']

# Watson API
USER_NAME = environ['USER_NAME']
PASSWORD = environ['PASSWORD']

def get_consumer_key():
    return CONSUMER_KEY

def get_consumer_secret():
    return CONSUMER_SECRET

def get_access_token():
    return ACCESS_TOKEN

def get_access_secret():
    return ACCESS_SECRET

def get_username():
    return USER_NAME

def get_password():
    return PASSWORD
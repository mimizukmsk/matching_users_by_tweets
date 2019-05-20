// match chart's data
var matchData = {
  labels: matchDataLabels,
  datasets: [{
    label: "一致度",
    backgroundColor: "rgba(255, 99, 132, 0.2)",
    borderColor: "rgba(255, 99, 132, 1)",
    data: matchDataSets
  }]
};
// users chart's data
var usersData = {
  labels: usersDataLabels,
  datasets: [{
    label: usersName[0],
    backgroundColor: "rgba(99, 132, 255, 0.2)",
    borderColor: "rgba(99, 132, 255, 1)",
    data: usersDataUser1Sets
  }, {
    label: usersName[1],
    backgroundColor: "rgba(132, 255, 99, 0.2)",
    borderColor: "rgba(132, 255, 99, 1)",
    data: usersDataUser2Sets
  }]
};

// render target
var matchChart = document.getElementById("match-chart");
var usersChart = document.getElementById("users-chart");

// render chart
new Chart(matchChart, {
  type: 'radar',
  data: matchData,
  options: {
    scale: {
      pointLabels: {
        fontSize: 12
      },
      ticks: {
        stepSize: 20,
        beginAtZero: true,
        min: 0,
        max: 100,
      }
    }
  }
});
new Chart(usersChart, {
  type: 'radar',
  data: usersData,
  options: {
    scale: {
      pointLabels: {
        fontSize: 12
      },
      ticks: {
        stepSize: 20,
        beginAtZero: true,
        min: 0,
        max: 100,
      }
    }
  }
});
var data;
data = {}

if (data === undefined || data.length == 0) {
    fetch('/query')
        .then(function (response) {
            return response.json();
        })
        .then(function (json) {
            data = json;
        })
}

console.log(data);

var barDom = document.getElementById('barchart');

var barChart = new Chart(barDom, {
    type: 'horizontalBar',
    data: {
        labels: ['Ice Cream & Frozen Yogurt', 'Korean', 'American (Traditional)'],
        datasets: [{
            data: [2, 2, 1],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 0.4)',
                'rgba(54, 162, 235, 0.4)',
                'rgba(255, 206, 86, 0.4)'
            ],
            borderWidth: 1,
            label: '',
            barThickness: 0.2,
            categoryPercentage: 0.5,
            barPercentage: 0.5
        }]
    },
    options: {
        legend: {
            display: false
        },
        scales: {
            xAxes: [{
                ticks: {
                    beginAtZero: true
                },
                gridLines: {
                    offsetGridLines: false
                }
            }]
        }
    }
});

const plugins = [{
    beforeInit: (chart) => {
        const dataset = chart.data.datasets[0];
        chart.data.labels = [dataset.label];
        dataset.data = [dataset.percent, 10 - dataset.percent];
    }
}]

const options = {
    legend: {
        display: false,
    },
    tooltips: {
        filter: tooltipItem => tooltipItem.index == 0,
        enabled: tooltipItem => tooltipItem.index == 0
    }
}

var backgroundColors = ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'];
var borderColors = ['rgba(255, 99, 132, 0.4)', 'rgba(54, 162, 235, 0.4)', 'rgba(255, 206, 86, 0.4)']

function htmlDecode(input) {
    var doc = new DOMParser().parseFromString(input, "text/html");
    return doc.documentElement.textContent;
}

for (i = 1; i <= 6; i++) { 
    var donutDom = document.getElementById('donutchart' + i);
    var donutChart = new Chart(donutDom, {
        type: 'doughnut',
        data: {
            datasets: [{
                label: htmlDecode(donutDom.previousElementSibling.innerHTML),
                percent: donutDom.getAttribute('value'),
                backgroundColor: [backgroundColors[(i-1)%3]],
                borderColor: [borderColors[(i-1)%3]],
                borderWidth: 1
            }]
        },
        plugins: plugins,
        options: options
    });
}
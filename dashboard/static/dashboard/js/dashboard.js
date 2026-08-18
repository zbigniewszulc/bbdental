var monthlyOrderLabels = JSON.parse(
    document.getElementById('monthly-order-labels').textContent
);
var monthlyOrderTotals = JSON.parse(
    document.getElementById('monthly-order-totals').textContent
);

var monthlyOrdersChart = document.getElementById(
    'monthly-orders-chart'
);

new Chart(monthlyOrdersChart, {
    type: 'bar',
    data: {
        labels: monthlyOrderLabels,
        datasets: [{
            label: 'Orders',
            data: monthlyOrderTotals,
            backgroundColor: '#0d6efd'
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

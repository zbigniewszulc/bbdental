// MONTHLY ORDERS CHART
// Get the month names added to the template by Django
var monthlyOrderLabels = JSON.parse(
    document.getElementById('monthly-order-labels').textContent
);

// Get the number of orders placed in each month
var monthlyOrderTotals = JSON.parse(
    document.getElementById('monthly-order-totals').textContent
);

// Find the canvas where the monthly orders chart will be displayed
var monthlyOrdersChart = document.getElementById(
    'monthly-orders-chart'
);

// Create a bar chart showing the number of orders for each month
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
        // Resize the chart when the screen size changes
        responsive: true,
        scales: {
            y: {
                // Start the number of orders from zero
                beginAtZero: true
            }
        }
    }
});

// TOP SELLING PRODUCTS CHART 
// Get the product names added to the template by Django
var topSellingProductLabels = JSON.parse(
    document.getElementById('top-selling-product-labels').textContent
);

// Get the quantity sold for each product
var topSellingProductTotals = JSON.parse(
    document.getElementById('top-selling-product-totals').textContent
);

// Find the canvas where the chart will be displayed
var topSellingProductsChart = document.getElementById(
    'top-selling-products-chart'
);

// Create a horizontal chart for the top-selling products
new Chart(topSellingProductsChart, {
    type: 'bar',
    data: {
        labels: topSellingProductLabels,
        datasets: [{
            label: 'Quantity Sold',
            data: topSellingProductTotals,
            backgroundColor: '#198754'
        }]
    },
    options: {
        // Display the product names on the vertical axis
        indexAxis: 'y',
        responsive: true,
        scales: {
            // Start the quantity scale from zero
            x: {
                beginAtZero: true
            }
        }
    }
});
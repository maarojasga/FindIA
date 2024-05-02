document.addEventListener('DOMContentLoaded', function () {
    Highcharts.chart('container', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Ingresos vs Gastos'
        },
        xAxis: {
            categories: ['Categorías']
        },
        yAxis: {
            title: {
                text: 'Monto'
            }
        },
        series: [{
            name: 'Ingresos',
            data: [{{ total_ingresos }}],
            color: 'green'
        }, {
            name: 'Gastos',
            data: [{{ total_gastos }}],
            color: 'red'
        }]
    });

    document.getElementById('viewSwitch').addEventListener('change', function() {
        var chartDiv = document.getElementById('container');
        var movementsList = document.getElementById('movementsList');
        if (this.checked) {
            chartDiv.style.display = 'none';
            movementsList.style.display = 'block';
        } else {
            chartDiv.style.display = 'block';
            movementsList.style.display = 'none';
        }
    });
});

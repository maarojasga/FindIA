document.addEventListener('DOMContentLoaded', function () {
    Highcharts.chart('container', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Ingresos vs Gastos'
        },
        xAxis: {
            categories: ['Ingresos', 'Gastos']
        },
        yAxis: {
            title: {
                text: 'Monto'
            }
        },
        series: [{
            name: 'Categorías',
            data: [{{ total_ingresos|safe }}, {{ total_gastos|safe }}]
        }]
    });
});
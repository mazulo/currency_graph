$(".currency").click(function() {

    var currency_base = $(this).attr("value");

    $.get('/currencies/', {base: currency_base}, function(data) {
        var chart_categories = [];
        var chart_values = [];

        $.each(data.currencies, function(index, element) {
            chart_categories.push(element.fields.date);
            chart_values.push(parseFloat(element.fields.value));
        });

        $(function () {
            Highcharts.chart('container', {
                title: {
                    text: 'Currency graph'
                },

                subtitle: {
                    text: 'Variation of BRL -> ' + currency_base
                },


                xAxis: {
                    categories: chart_categories
                },

                series: [{
                    data: chart_values
                }]
            });
        });
    });
});

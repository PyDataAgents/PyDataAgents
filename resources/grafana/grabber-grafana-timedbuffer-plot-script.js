//console.log(data);
//console.log(data.series[0].fields[0].values);
var trace = {
    x: data.series[0].fields[0].values,
    y: data.series[0].fields[1].values,
};

var layout = {
    title: '#TITLE',
    xaxis: {
        title: {
            text: 'X'
        },
    },
    yaxis: {
        title: {
            text: 'Y'
        }
    }
}

return {data:[trace],layout: layout};
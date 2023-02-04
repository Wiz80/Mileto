function plotTimeSeries(data, min, max, inicio, final){
  var time = data.map(function(item) { return item.time; });
  var testRealValues = data.map(function(item) { return item.testRealValues; });
  var testPredictions = data.map(function(item) { return item.testPredictions; });

  var trace1 = {
  type: "scatter",
  mode: "lines",
  name: "Demanda Real",
  x: time,
  y: testRealValues,
  line: {color: '#7F7F7F'}
  }

  var trace2 = {
  type: "scatter",
  mode: "lines",
  name: "Demanda Predecida",
  x: time,
  y: testPredictions,
  line: {color: '#17BECF'}
  }

  var dataPlot = [trace1,trace2];

  var layout = {
    title: {  text: 'Predicción y valor real de demanda de energía (MW)',
            font: {
              family: 'SF Pro Display',
              weight: 700,
              size: 20
            },
          },
    xaxis: {
      autorange: true,
      range: [inicio, final],
      rangeselector: {buttons: [
          {
            count: 1,
            label: '1m',
            step: 'month',
            stepmode: 'backward'
          },
          {
            count: 6,
            label: '6m',
            step: 'month',
            stepmode: 'backward'
          },
          {step: 'all'}
        ]},
      rangeslider: {range: [inicio, final]},
      type: 'date'
    },
    yaxis: {
      autorange: true,
      range: [min, max],
      type: 'linear'
    }
  };
  Plotly.newPlot('plot', dataPlot, layout);
        
}



function plotTestTimeSeries(data, min, max, inicio, final){
    var time = data.map(function(item) { return item.time; });
    var testPredictions = data.map(function(item) { return item.testPredictions; });
  
    var trace2 = {
    type: "scatter",
    mode: "lines",
    name: "Demanda Predecida",
    x: time,
    y: testPredictions,
    line: {color: '#01E1D4'}
    }
  
    var dataPlot = [trace2];
  
    var layout = {
      title: {  text: 'Predicción de demanda de energía (MW)',
              font: {
                family: 'SF Pro Display',
                weight: 'bold',
                size: 15
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
function time_series(file_name, inicio, final, min, max){

    console.log(file_name);
    console.log(inicio);
    console.log(final);
    console.log(min);
    console.log(max);
    
    d3.csv(`./models/${file_name}.csv`, function(err, rows){

        function unpack(rows, key) {
        return rows.map(function(row) { return row[key]; });
      }
      
      
      var trace1 = {
        type: "scatter",
        mode: "lines",
        name: 'Target values',
        x: unpack(rows, 'time'),
        y: unpack(rows, 'Target_values'),
        line: {color: '#17BECF'}
      }
      
      var trace2 = {
        type: "scatter",
        mode: "lines",
        name: 'Target predictions',
        x: unpack(rows, 'time'),
        y: unpack(rows, 'Target_predictions'),
        line: {color: '#7F7F7F'}
      }
      
      var data = [trace1,trace2];
      
      var layout = {
        title: 'Time Series forecasting',
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
      
      Plotly.newPlot('myDiv', data, layout);
      })
}


function time_series_rela(file_name, inicio, final, min, max){
    d3.csv(`./models/${file_name}.csv`, function(err, rows){

    function unpack(rows, key) {
    return rows.map(function(row) { return row[key]; });
    }


    var trace1 = {
    type: "scatter",
    mode: "lines",
    name: 'AAPL High',
    x: unpack(rows, 'time'),
    y: unpack(rows, 'Target_values'),
    line: {color: '#17BECF'}
    }

    var trace2 = {
    type: "scatter",
    mode: "lines",
    name: 'Target predictions',
    x: unpack(rows, 'time'),
    y: unpack(rows, 'Target_predictions'),
    line: {color: '#7F7F7F'}
    }

    var data = [trace1,trace2];

    var layout = {
    title: 'Basic Time Series',
    };

    Plotly.newPlot('myDiv', data, layout);
    })

}
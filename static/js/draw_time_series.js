function time_series(file_name, inicio, final, min, max){

    //d3.csv("https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv", function(err, rows){

    d3.csv("https://docs.google.com/spreadsheets/d/14CpcTBfOeon27ZJkTkfN8k5lJtgQmvYw/edit?usp=share_link&ouid=111326907896635334350&rtpof=true&sd=true", function(err, rows){  

    function unpack(rows, key) {
    return rows.map(function(row) { return row[key]; });
    }

    
    var trace1 = {
      type: "scatter",
      mode: "lines",
      name: 'AAPL High',
      x: unpack(rows, 'Date'),
      y: unpack(rows, 'AAPL.High'),
      line: {color: '#17BECF'}
    }

    var trace2 = {
      type: "scatter",
      mode: "lines",
      name: 'AAPL Low',
      x: unpack(rows, 'Date'),
      y: unpack(rows, 'AAPL.Low'),
      line: {color: '#7F7F7F'}
    }

    var data = [trace1,trace2];

    var layout = {
      title: 'Time Series with Rangeslider',
      xaxis: {
        autorange: true,
        range: ['2015-02-17', '2017-02-16'],
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
        rangeslider: {range: ['2015-02-17', '2017-02-16']},
        type: 'date'
      },
      yaxis: {
        autorange: true,
        range: [86.8700008333, 138.870004167],
        type: 'linear'
      }
    };

    Plotly.newPlot('myDiv', data, layout);
    })

}


function time_series_rela(file_name, inicio, final, min, max){
    d3.csv("https://docs.google.com/spreadsheets/d/1LuSWMLw7L7Hw7fpHUQ9abYCvzmlU1e2C/edit?usp=share_link&ouid=111326907896635334350&rtpof=true&sd=true", function(err, rows){

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


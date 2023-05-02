function plotTimeSeries(data, names, nameMinModel, min, max, inicio, final){
    var time = data.map(function(item) { return item.time; });
    const colorList = [
        "#FFB6C1", "#FF69B4", "#FFC0CB", "#FFA07A", "#FF8C00",
        "#FFA500", "#FFD700", "#FFFF00", "#9ACD32", "#7CFC00",
        "#00FF7F", "#32CD32", "#00FA9A", "#40E0D0", "#00BFFF",
        "#1E90FF", "#0000FF", "#4169E1", "#8A2BE2", "#FF00FF",
        "#BA55D3", "#9370DB", "#663399", "#8B008B", "#FF1493",
        "#DC143C", "#FF0000", "#B22222", "#FF4500", "#FF6347",
        "#CD5C5C", "#F08080", "#FA8072", "#FFDAB9", "#FFE4B5",
        "#EEE8AA", "#F0E68C", "#FFFFE0", "#FAFAD2", "#D3D3D3",
        "#A9A9A9", "#808080", "#89F9F9", "#7FFC79", "#FF6EB4",
        "#FF69AF", "#FF8C9F", "#FFA07A", "#FFA500", "#FFC154",
        "#FFD700", "#EEC900", "#9ACD32", "#7FFF00", "#00FF7F",
        "#32CD32", "#00FA9A", "#00CED1", "#40E0D0", "#00BFFF",
        "#1E90FF", "#0000FF", "#7B68EE", "#8A2BE2", "#FF00FF",
        "#FF69B4", "#FF1493", "#DC143C", "#FF0000", "#B22222",
        "#FF4500", "#FF6347", "#CD5C5C", "#F08080", "#FA8072",
        "#FFA07A", "#FFDAB9", "#EEE8AA", "#F0E68C", "#FFFFE0",
        "#FAFAD2", "#D3D3D3", "#A9A9A9", "#808080", "#40F0FF",
        "#9F0920", "#800080", "#C71585", "#9370DB", "#8B008B",
        "#4B0082", "#483D8B", "#191970", "#00BFFF", "#1E90FF",
        "#00CED1", "#40E0D0", "#7FFFD4", "#00FF7F", "#32CD32",
        "#9ACD32"
      ];
    
    var dataPlot = [];
    var dataMinPlot = [];
    
    for(var i = 0; i< names.length; i++){
        console.log(names[i])
        var testRealValues = data.map(function(item) { return item[names[i]]; });
        const randomColor = colorList[Math.floor(Math.random() * colorList.length)];
        
        var trace = {
            type: "scatter",
            mode: "lines",
            name: names[i],
            x: time,
            y: testRealValues,
            line: {color: randomColor}
        }

        if(names[i] == nameMinModel || names[i] == 'realDemand'){
            dataMinPlot.push(trace);
        }  

        dataPlot.push(trace);
    }

  
    var layout = {
      title: {  text: 'Predicción y valor real de demanda de energía (MW)',
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
    Plotly.newPlot('plot2', dataMinPlot, layout);
  }
  
  
  
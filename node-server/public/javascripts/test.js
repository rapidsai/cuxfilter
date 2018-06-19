var data = JSON.parse(document.getElementById('hid-val').innerHTML);

var cols = document.getElementById("hid-col").innerHTML;

genCols(cols);
genPlot(data,'histogram');

function genPlot(data,type){
    console.log(data['A']);
    var d = [{
        x: data['B'],
        y: data['A'],
        type: type
    }
    ]
   Plotly.newPlot('myDiv', d);
}

function genCols(cols){
    var colDiv = document.getElementById('cols');
    colDiv.innerHTML = "Columns: "+cols.toString(); 
}
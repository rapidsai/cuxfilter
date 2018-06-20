var data = '';

var cols = document.getElementById("hid-col").innerHTML;
var curr_col ='';
var X=0,Y=0;
var type='bar';
genCols(cols);

function genPlot(X,Y,type){
    //just for demonstration purposes, hist visualizes better when X and Y coordinates are swapped: opposite for bar
    if(type == "histogram"){
        var temp = X;
        X = Y;
        Y = X;
    }
    var d = [{
        x: X,
        y: Y,
        type: type
    }
    ]
   Plotly.newPlot('myDiv', d);
}

$('input[type=radio][name=X]').change(function(){
    
    if(curr_col !== $(this).val()){
        var data = JSON.stringify({ col: $(this).val()});
    
        $.post("/calc/getHist", { col: $(this).val()},function(data,status){
            data = JSON.parse(data);
            X = data['A'];
            Y = data['B'];
            console.log(X);
            genPlot(X,Y,type);
            curr_col = $(this).val()
        });
    }
    
});

$("#hist").on("click",function(){
    if(type !== "histogram"){
        type = 'histogram';
        genPlot(X,Y,type);
    }
});
$("#bar").on("click",function(){
    if(type !== "bar"){
        type = 'bar';
        genPlot(X,Y,type);
    }
});



function genCheckBox(val,text){
    if(val){
        $('#cols-x').append('<input type="radio" name="X" value='+text+'  /> ' + text + '<br>');
    }else{
        $('#cols-x').append('<input type="radio" name="X" value='+text+' /> ' + text + '<br>');
    }
}

function genCols(cols){
    var colDiv = document.getElementById('hid-col');
    var a = colDiv.innerHTML.replace(/'/g, '"');
    a = JSON.parse(a);
    X = data[a[0]];
    Y = data[a[1]];
    console.log(type);
    for(var i=0; i< a.length; i++){
        genCheckBox(false, a[i]);
    }
}
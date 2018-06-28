var data = '';

var cols = document.getElementById("hid-col").innerHTML;
var curr_col ='';
var X=0,Y=0;
var type='histogram';
var processing = 'pandas';
var load_type = 'csv';

function getCols(){
    var data = {
        processing: processing,
        load_type: load_type
    };

    $.post("/calc/getColumns",data, function(data,status){
        console.log(typeof data);
        genCols(data);
    });
}

function genPlot(X,Y,type){
 
    var d = [{
        x: X,
        y: Y,
        mode: 'markers',
        type: type
    }
    ]
   Plotly.newPlot('myDiv', d);
}

$('input[type=radio][name=processing]').change(function() {
    processing = $(this).val();
});

$('input[type=radio][name=load_type]').change(function() {
    load_type = $(this).val();
});

function initiateListeners(val){
    $('input[type=radio][name=X][value='+val+']').change(function(){
        console.log("");
        if(curr_col !== $(this).val()){
            var data = {
                col: $(this).val(),
                processing: processing,
                load_type: load_type
            };
            $.post("/calc/getHist", data,function(data,status){
                data = JSON.parse(data);
                X = data['A'];
                Y = data['B'];
                console.log(X);
                genPlot(X,Y,type);
                curr_col = $(this).val()
            });
        }
        
    });
}

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

$("#scatter").on("click",function(){
    if(type !== "scatter"){
        type = 'scatter';
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
    var a = cols.replace(/'/g, '"');
    a = JSON.parse(a);
    X = data[a[0]];
    Y = data[a[1]];
    console.log(type);
    for(var i=0; i< a.length; i++){
        if(jQuery(':radio[name=X][value='+a[i]+']').length===0){
            genCheckBox(false, a[i]);
            initiateListeners(a[i]);
        }
    }
    
}
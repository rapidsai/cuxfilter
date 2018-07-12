var data = '';
var cols = document.getElementById("hid-col").innerHTML;
var curr_col ='';
var X=0,Y=0;
var type='histogram';
var processing = 'numba';
var load_type = 'arrow';
var current_chart_col = '';
var responseTime,totalTime;
var persistentConnStatus = false;
var url = '';

$.get('/socket-calc/getStatus',{}, function(data,status){
    if(data === 'active'){
        persistentConnStatus = true;
        $("#persistentConnStatus").text("Socket connection already established");
    }
});

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURI(results[1]) || 0;
    }
}

//static listeners
$('input[type=radio][name=processing]').change(function() {
    processing = $(this).val();
});

$('input[type=radio][name=load_type]').change(function() {
    load_type = $(this).val();
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

$("#scatter").on("click",function(){
    if(type !== "scatter"){
        type = 'scatter';
        genPlot(X,Y,type);
    }
});

function getCols(){
    var data = {};

    url = '/socket-calc/getColumns';
    
    if(!persistentConnStatus){
        url = '/calc/getColumns';
        data.processing = processing,
        data.load_type = load_type,
        data.file = $.urlParam('file');
    }

    responseTime = Date.now();

    $.post(url,data, function(data,status){
        console.log(typeof data);
        genCols(data);
        $('.genChart').show();
    
        totalTime = Date.now() - responseTime;
        $('#restime').text(totalTime);
    });
}

function getHist(){
    var data = {
        col: current_chart_col,
        processing: processing,
    };
    url = '/socket-calc/getHist';
    
    if(!persistentConnStatus){
        url = '/calc/getHist';
        data.file = $.urlParam('file');
        data.load_type = load_type;
    }

    responseTime = Date.now();
    $.post(url, data,function(data,status){
        data = JSON.parse(data);
        X = data['A'];
        Y = data['B'];
        console.log(X);
        
        totalTime = Date.now() - responseTime;
        $('#restime').text(totalTime);

        genPlot(X,Y,type);
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

function initiateListeners(val){
    $('input[type=radio][name=X][value='+val+']').change(function(){
        current_chart_col = $(this).val();        
    });
}

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

function persistentConnStart(){
    var data = {
        file: $.urlParam('file'),
    };
    $.get("/socket-calc/startConnection", data,function(data,status){
        $("#persistentConnStatus").text("Connected"+data);
        persistentConnStatus = true;
    });
}
function persistentConnEnd(){
    $.get("/socket-calc/stopConnection", data,function(data,status){
        $("#persistentConnStatus").text("Connection Ended");
        persistentConnStatus = false;
    });   
}
var data = '';
var cols = document.getElementById("hid-col").innerHTML;
var curr_col ='';
var X=0,Y=0;
var type='bar';
var processing = 'numba';
var load_type = 'arrow';
var current_chart_col = '';
var responseTime,totalTime;
var persistentConnStatus = false;
var url = '';
var timeStr = {
    front_end: '',
    node_server_request_time:'',
    py_script_compute_time:''
}

function displayTimings(totalTimeFE,totalTimePyScript,totalTimeNodeServer){
    timeStr.front_end = "-ms";//totalTimeFE+"ms";
    timeStr.node_server_request_time = totalTimeNodeServer+"ms";
    timeStr.py_script_compute_time = totalTimePyScript*1000 + "ms";
    console.log(timeStr);
    var obj = timeStr;
    var str = "Front end: "+timeStr.front_end+"\nNodeServer: "+timeStr.node_server_request_time+"\nPyScriptCompute: "+timeStr.py_script_compute_time;
    $('#restime').text(str);

}

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURI(results[1]) || 0;
    }
}

$.get('/socket-calc/getStatus',{file: $.urlParam('file')}, function(data,status){
    if(data === 'active'){
        persistentConnStatus = true;
        $("#persistentConnStatus").text("Socket connection already established");
    }
});

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
    var data = {
        file: $.urlParam('file')
    };

    url = '/socket-calc/getColumns';

    if(!persistentConnStatus){
        url = '/calc/getColumns';
        data.processing = processing,
        data.load_type = load_type
    }

    responseTime = Date.now();

    $.post(url,data, function(data,status){
        totalTime = Date.now() - responseTime;
        console.log(data);
        data = JSON.parse(data);
        pyData = data.pyData.split(":::");
        var coldata = pyData[0];
        genCols(coldata);
        $('.genChart').show();

        displayTimings(totalTime,pyData[1],data.nodeServerTime);
    });
}

function getHist(){
    var data = {
        col: current_chart_col,
        processing: processing,
        bins:12,
        file: $.urlParam('file')
    };
    url = '/socket-calc/getHist';

    if(!persistentConnStatus){
        url = '/calc/getHist';
        data.load_type = load_type;
    }

    $.post({
        url: url,
        data:data,
        responseTime: Date.now(),
        complete: function(data){
                totalTime = Date.now() - responseTime;
                data = data.responseText;
                data = JSON.parse(data);
                pyData = data.pyData.split(":::");
                console.log(pyData);
                X = JSON.parse(pyData[0])['A'];
                Y = JSON.parse(pyData[0])['B'];
                console.log(X);
                genPlot(X,Y,type);
                displayTimings(totalTime,pyData[1],data.nodeServerTime);
            }
        });
}

function getAllHist(col){
    var data = {
        col: col,
        processing: processing,
        bins:12,
        file: $.urlParam('file')
    };
    url = '/socket-calc/getHist';

    if(!persistentConnStatus){
        url = '/calc/getHist';
        data.load_type = load_type;
    }

    $.post({
        url: url,
        data:data,
        responseTime: Date.now(),
        complete: function(data){
                totalTime = Date.now() - responseTime;
                data = data.responseText;
                data = JSON.parse(data);
                pyData = data.pyData.split(":::");
                console.log(pyData);
                X = JSON.parse(pyData[0])['A'];
                Y = JSON.parse(pyData[0])['B'];
                console.log(X);
                genPlot(X,Y,type);
                displayTimings(totalTime,pyData[1],data.nodeServerTime);
            }
        });
}

function test(){
  getAllHist('sourceid');
  getAllHist('dstid');
  getAllHist('mean_travel_time');
  getAllHist('standard_deviation_travel_time');
  getAllHist('source_long');
  getAllHist('source_lat');
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
        file: $.urlParam('file')
    };
    $.get("/socket-calc/startConnection", data,function(data,status){
        data = JSON.parse(data);
        console.log(data);
        $("#persistentConnStatus").html("Connected"+data.pyData);
        persistentConnStatus = true;
    });
}
function persistentConnEnd(){
    var data = {
        file: $.urlParam('file')
    };
    $.get("/socket-calc/stopConnection", data,function(data,status){
        console.log(data);
        $("#persistentConnStatus").html("Connection Ended");
        persistentConnStatus = false;
    });
}

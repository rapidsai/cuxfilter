var data = '';

var cols = document.getElementById("hid-col").innerHTML;
var curr_col ='';
var X=0,Y=0;
var type='bar';


function getCols(){
    $.post("/calc/getColumns", function(data,status){
        console.log(typeof data);
        genCols(data);
    });
}

function genPlot(X,Y,type){
 
    var d = [{
        x: X,
        y: Y,
        type: type
    }
    ]
   Plotly.newPlot('myDiv', d);
}

function initiateListeners(){
    $('input[type=radio][name=X]').change(function(){
        console.log("");
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
        genCheckBox(false, a[i]);
    }
    initiateListeners();
}
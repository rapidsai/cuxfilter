var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 
var spawn = require('child_process').spawn;
var net = require('net');

var HOST = '127.0.0.1';
var PORT = 3001;
var startTime, endTime;
var pyClient = {}, pyServer = {};
var tryAgain = 0;
var getHistEvent = {};
var response = {
    pyData:'',
    nodeServerTime:''
};
router.get('/', function(req, res) {
    var sessId = req.session.id;   
    console.log(sessId);
    res.render('dashboard',{title:"Socket-Calc api home page",val: JSON.stringify({hello:"World"}),cols:''});
}); 

router.get('/getStatus', function(req,res){
    var sessId = req.session.id;
    var file = req.query.file;
    console.log(sessId+file);
    if(pyClient[sessId+file]){
        console.log("status:"+pyClient[sessId+file].readable);
        if(!pyClient[sessId+file].readable){
            res.end("inactive");
        }else{
            res.end("active");
        }
    }else{
        res.end("inactive");
    }
    
});

router.get('/startConnection', function(req,res){
    // console.log(req);
    tryAgain=0;
    var sessId = req.session.id;
    console.log(sessId);
    var file = req.query.file;
    pyServer[sessId+file] = spawn('python3', ['../python_scripts/persistent-server-script.py']);
    pyServer[sessId+file].stdout.on('data', function(data) {
        console.log('PyServer stdout '+data);
        //Here is where the output goes
    });
    
    
    getHistEvent[sessId+file] = 0;
    pyClient[sessId+file] = new net.Socket();
    setTimeout(function(){
        pyClient[sessId+file].connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
        });
    },1000);
    pyClient[sessId+file].on('error',function(err){
        console.log(err);
        if(tryAgain === 0){
            setTimeout(function(){
                pyClient[sessId+file].connect(PORT, HOST, function() {
                console.log('CONNECTED TO: ' + HOST + ':' + PORT);
             });
           },1000);
           tryAgain=1;
         }else{
        var response = {
            pyData: "  -> something went wrong, try connection again",
            nodeServerTime: Date.now() - startTime
        }
        res.end(JSON.stringify(response));
        }

    });
    load_data(sessId,file, function(val){
        console.log("i should not reach here");
        console.log("received data from pyscript");
        var response = {
            pyData: Buffer.from(val).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        // console.log(response);
        pyClient[sessId+file].removeAllListeners(['data']);
        res.end(JSON.stringify(response));
    });
    
});

function load_data(sessId,file,callback){
    pyClient[sessId+file].on("data", function(val){
        callback(val);
    });
    pyClient[sessId+file].on("connect", function(){
        startTime = Date.now();
        console.log(startTime);
        pyClient[sessId+file].write('read:::'+file);
    });
}
router.get('/stopConnection', function(req,res){
    var sessId = req.session.id;
    var file = req.query.file;
    console.log("destroying connection");
    if(!pyClient[sessId+file].readable){
        var response = {
            pyData: "already destroyed"
        }
        res.end(JSON.stringify(response));
    }
    pyClient[sessId+file].on('close',function(){
        if(!pyClient[sessId+file].readable){
            var response = {
                pyData: "session destroyed"
            }
            res.end(JSON.stringify(response));
        }
    });
    pyClient[sessId+file].destroy();
});

router.post('/getColumns', function(req,res){
    // console.log("here in getColumns");
    var sessId = req.session.id;
    var file = req.body.file;
    startTime = Date.now();
    getColumns(sessId,file, function(cols){
        // console.log(cols);
        var response = {
            pyData: Buffer.from(cols).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        res.end(JSON.stringify(response));
    });
});

router.post('/getHist', function(req,res){
    console.log("starting the getHist request");
    var sessId = req.session.id;
    var processing = req.body.processing;
    var columnName = req.body.col;
    var bins = req.body.bins;
    var file = req.body.file;
    startTime = Date.now();
    console.log("calling pyscript now");
    getHist(sessId,file, processing,columnName,bins, function(hist){
        console.log("received the response from pyscript");
        response.pyData= Buffer.from(hist).toString('utf8');
        response.nodeServerTime = Date.now() - startTime;
        console.log("sending response to client");
        res.end(JSON.stringify(response));
    });
});


function getColumns(sessId,file, callback){
    pyClient[sessId+file].on("data", function(cols){
        pyClient[sessId+file].removeAllListeners(['data']);
        callback(cols);
    });
    pyClient[sessId+file].write("columns:::"+sessId);
}

function getHist(sessId, file, processing,columnName,bins, callback){
    console.log("inside the getHist function");
    try{
        console.log(pyClient[sessId+file]._events.data.toString());
        console.log(process.memoryUsage());
    }catch(e){
        // console.log(e);
    }
    pyClient[sessId+file].removeAllListeners(['data']);

    pyClient[sessId+file].on("data", function(cols){
        console.log("inside the on data callback function");
        getHistEvent[sessId+file] =1;
        callback(cols);
    });
    
    console.log("set up the callback function");
    console.log(pyClient[sessId+file].readable);
    var query = "hist:::"+sessId+":::"+processing+":::"+columnName+":::"+bins;
    console.log(query);
    pyClient[sessId+file].write(query);
}


module.exports = router;

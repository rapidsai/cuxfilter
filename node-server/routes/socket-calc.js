var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 
var spawn = require('child_process').spawn;
var net = require('net');

var HOST = '127.0.0.1';
var PORT = 3001;
var startTime, endTime;
var pyClient;
var tryAgain = 0;

router.get('/', function(req, res) {
    var sessId = req.session.id;   
    res.render('dashboard',{title:"Socket-Calc api home page",val: JSON.stringify({hello:"World"}),cols:''});
}); 

router.get('/getStatus', function(req,res){
    var sessId = req.session.id;
    console.log("status:"+pyClient.readable);
    if(!pyClient.readable){
        res.end("inactive");
    }else{
        res.end("active");
    }
});

router.get('/startConnection', function(req,res){
    // console.log(req);
    var sessId = req.session.id;
    var file = req.query.file;
    var pyServer = spawn('python3', ['../python-scripts/persistent-server-script.py']);
    pyClient = new net.Socket();
    pyClient.connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
        startTime = Date.now();
        console.log(startTime);
        pyClient.write('read:::'+file);
    });
    pyClient.on('error',function(err){
        console.log(err);
        if(tryAgain === 0){
            setTimeout(function(){
              pyClient.connect(PORT, HOST, function() {
              console.log('CONNECTED TO: ' + HOST + ':' + PORT);
              startTime = Date.now();
              console.log(startTime);
              pyClient.write('read:::'+file);
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
    pyClient.on('data', function(val){
        console.log("received data from pyscript");
        var response = {
            pyData: Buffer.from(val).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        console.log(response);
        res.end(JSON.stringify(response));
    });
});

router.get('/stopConnection', function(req,res){
    var sessId = req.session.id;
    console.log("destroying connection");
    if(!pyClient.readable){
        var response = {
            pyData: "already destroyed"
        }
        res.end(JSON.stringify(response));
    }
    pyClient.on('close',function(){
        if(!pyClient.readable){
            var response = {
                pyData: "session destroyed"
            }
            res.end(JSON.stringify(response));
        }
    });
    pyClient.destroy();
});

router.post('/getColumns', function(req,res){
    // console.log("here in getColumns");
    var sessId = req.session.id;
    startTime = Date.now();
    getColumns(sessId, function(cols){
        console.log(cols);
        var response = {
            pyData: Buffer.from(cols).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        res.end(JSON.stringify(response));
    });
});

router.post('/getHist', function(req,res){
    console.log(req.body);
    var sessId = req.session.id;
    var processing = req.body.processing;
    var columnName = req.body.col;
    startTime = Date.now();
    getHist(sessId,processing,columnName, function(hist){
        console.log(hist);
        var response = {
            pyData: Buffer.from(hist).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        res.end(JSON.stringify(response));
        // res
    });
});


function getColumns(sessId,callback){
    pyClient.on("data", function(cols){
        callback(cols);
    });
    pyClient.write("columns:::"+sessId);
}

function getHist(sessId,processing,columnName,callback){
    pyClient.on("data", function(cols){
        callback(cols);
    });
    pyClient.write("hist:::"+sessId+":::"+processing+":::"+columnName);
}


module.exports = router;

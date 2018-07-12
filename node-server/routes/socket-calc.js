var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 
var spawn = require('child_process').spawn;
var net = require('net');

var HOST = '0.0.0.0';
var PORT = 3001;

var pyClient;

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
    console.log(req);
    var sessId = req.session.id;
    var file = req.query.file;
    var pyServer = spawn('python', ['../python-scripts/persistent-server-script.py']);
    pyClient = new net.Socket();
    pyClient.connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
        pyClient.write('read:::'+file);
    });
    pyClient.on('data', function(val){
        res.end(val);
    });
});

router.get('/stopConnection', function(req,res){
    var sessId = req.session.id;
    console.log("destroying connection");
    pyClient.on('close',function(){
        if(!pyClient.readable){
            res.end("session destroyed");
        }
    });
    pyClient.destroy();
});

router.post('/getColumns', function(req,res){
    // console.log("here in getColumns");
    var sessId = req.session.id;

    getColumns(sessId, function(cols){
        console.log(cols);
        res.end(cols);
    });
});

router.post('/getHist', function(req,res){
    console.log(req.body);
    var sessId = req.session.id;
    var processing = req.body.processing;
    var columnName = req.body.col;
    getHist(sessId,processing,columnName, function(hist){
        console.log(hist);
        res.end(hist);
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

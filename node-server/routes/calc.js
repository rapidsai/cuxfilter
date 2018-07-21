var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 
var startTime, endTime;


router.get('/', function(req, res) {
    var sessId = req.session.id;   
    res.render('dashboard',{title:"File Uploaded Successfully",val: JSON.stringify({hello:"World"}),cols:''});
}); 

router.post('/getColumns', function(req,res){
    var sessId = req.session.id;
    // console.log(req.body);
    var file = req.body.file;
    var processing = req.body.processing;
    var load_type = req.body.load_type;
    // console.log('here1');
    getColumns(sessId,file,processing,load_type, function(cols){
        // console.log('here4');
        var response = {
            pyData: Buffer.from(cols).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        res.end(JSON.stringify(response));
    });
});

router.post('/getHist', function(req,res){
    var sessId = req.session.id;
    var file = req.body.file;
    var colName = req.body.col;
    var processing = req.body.processing;
    var load_type = req.body.load_type;
    var bins = req.body.bins;
    console.log(req.body);
    getHist(sessId,file, colName,bins, processing,load_type, function(hist){
        var response = {
            pyData: Buffer.from(hist).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        res.end(JSON.stringify(response));
    });

});

function getColumns(sessId,file,processing,load_type,callback){
    // console.log('here2');
    var spawn = require('child_process').spawn;  
    var py = spawn('python3', ['../python-scripts/script.py', sessId,file,'columns', processing,load_type]);
    py.stdout.on('data', function(val){
        // console.log('here3');
        // console.log(val);
        callback(val);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
}

function getHist(sessId,file,colName,bins, processing,load_type, callback) {
    let chunks = [];
    
    var spawn = require('child_process').spawn;  
    var py = spawn('python3', ['../python-scripts/script.py', sessId, file,'hist',processing,load_type,colName,bins]);
    py.stdout.on('data', function(val){
        chunks.push(val);
	console.log(val);
    }).on('end', function() {
        let data = Buffer.concat(chunks);
        console.log(data);
        callback(data);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
}

module.exports = router;

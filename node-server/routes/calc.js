var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 


router.get('/', function(req, res) {
    var sessId = req.session.id;   
    res.render('dashboard',{title:"File Uploaded Successfully",val: JSON.stringify({hello:"World"}),cols:''});
}); 

router.post('/getColumns', function(req,res){
    var sessId = req.session.id;
    console.log(req.body);
    var processing = req.body.processing;
    var load_type = req.body.load_type;
    getColumns(sessId,processing,load_type, function(cols){
        res.send(cols);
    });
});

router.post('/getHist', function(req,res){
    var sessId = req.session.id;
    console.log(req.body);
    var colName = req.body.col;
    var processing = req.body.processing;
    var load_type = req.body.load_type;

    getHist(sessId,colName,processing,load_type, function(val){
        console.log(val);
        var value = JSON.parse(val);
        res.send(JSON.stringify(value));
    });

});

function getColumns(sessId,processing,load_type,callback){
    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['../python-scripts/script.py', sessId, 'columns', processing,load_type]);
    py.stdout.on('data', function(val){
        callback(val);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
}

function getHist(sessId,colName,processing,load_type, callback) {
    let chunks = [];
    
    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['../python-scripts/script.py', sessId, colName,'hist',processing,load_type]);
    py.stdout.on('data', function(val){
        chunks.push(val);
    }).on('end', function() {
        let data = Buffer.concat(chunks);
        callback(data);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
}

module.exports = router;

var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 



router.get('/', function(req, res) {
    
    var sessId = req.session.id;   
    getColumns(sessId, function(cols){
        res.render('dashboard',{title:"File Uploaded Successfully",val: JSON.stringify({hello:"World"}),cols:cols});
    });

}); 

router.post('/getHist', function(req,res){

    var sessId = req.session.id;
    var colName = req.body.col;
    console.log(sessId);
    console.log(colName);
    getHist(sessId,colName, function(val){
        console.log(val);
        var value = JSON.parse(val);
        res.send(JSON.stringify(value));
    });

});

function getColumns(sessId,callback){
    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['../python-scripts/script.py', sessId, 'columns']);
    py.stdout.on('data', function(val){
        callback(val);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
}

function getHist(sessId,colName, callback) {
    let chunks = [];
    
    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['../python-scripts/script.py', sessId, colName,'hist']);
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

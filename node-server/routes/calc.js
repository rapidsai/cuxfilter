var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 



router.get('/', function(req, res) {
    
    var sessId = req.session.id;

    getHist(sessId, function(val){
        var value = JSON.parse(val);
        getColumns(sessId, function(cols){
            res.render('dashboard',{title:"File Uploaded Successfully",val: JSON.stringify(value),cols:cols});
        });
    });

}); 

// router.get('/getColumns', function(req,res){

//     var sessId = req.session.id;

//     getColumns(sessId, function(val){
//         var value = JSON.parse(val);
//         res.send(JSON.stringify(value));
//     });

// });

function getColumns(sessId,callback){
    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['../python-scripts/script.py', sessId, 'columns']);
    py.stdout.on('data', function(val){
        callback(val);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
}

function getHist(sessId, callback) {

    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['../python-scripts/script.py', sessId, 'hist']);
    py.stdout.on('data', function(val){
        callback(val);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
  }

  module.exports = router;

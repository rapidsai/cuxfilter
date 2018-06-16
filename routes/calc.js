var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 



router.get('/', function(req, res) {

    let sessId = req.session.id;
    res.render("dashboard", {title: "file loaded!"});
    callPy(sessId, function(val){
        console.log("success");
    });

}); 


function callPy(sessId, callback) {

    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['python-scripts/script.py', sessId]);
    py.stdout.on('end', function(){
        callback(1);
    });

    py.stdin.write(JSON.stringify(sessId));
    py.stdin.end();
  }

  module.exports = router;

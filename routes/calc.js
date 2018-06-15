var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 



router.get('/', function(req, res) {

    let sessId = req.session.id;
    callPy(sessId, function(val){
        console.log("py script executed, value is");
        console.log(val);
        res.render("dashboard", {title: "file loaded!", value:val});
    });
}); 


function callPy(sessId, callback) {

    var spawn = require('child_process').spawn;  
    var py = spawn('python', ['python-scripts/script.py', sessId]);
    var dataString = '';
    py.stdout.on('data', function(value){
      console.log("here"+value);
      callback(value);
    });
    // py.stdout.on('end', function(){
    //   console.log("here");
    //   console.log('returned values=',dataString);
    //   return dataString;
    // });
    py.stdin.write(JSON.stringify(path));
    py.stdin.end();
  }

  module.exports = router;

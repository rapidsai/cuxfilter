var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 

router.get('/', function(req, res) {
    res.render("upload", {title: "file upload!"});
  }); 
  
router.post("/", function(req, res, next){
    console.log(req.files.path);
      if (req.files) {
        //   console.log(util.inspect(req.files));
          if (req.files[0].size === 0) {
                      return next(new Error("select a file?"));
          }
          console.log(req.files[0].path);
          fs.exists(req.files[0].path, function(exists) {
              if(exists) {
                  a = callPy(req.files[0].path);
                  res.end("Got your file!"+a);
              } else {
                  res.end("oh snap, that didn't work!");
              }
          });
      }
  });

  function callPy(path) {

    var spawn = require('child_process').spawn;  
    var py    = spawn('python', ['python-scripts/script.py']);
    var dataString = '';
    
    py.stdout.on('data', function(path){
      console.log("here"+path);
      dataString += path.toString();
    });
    py.stdout.on('end', function(){
      console.log("here");
      console.log('returned values=',dataString);
      return dataString;
    });
    py.stdin.write(JSON.stringify(path));
    py.stdin.end();
  }
  module.exports = router;
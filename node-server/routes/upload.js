var express = require('express');
var router = express.Router();
var util = require("util");
var fs = require("fs"); 

router.get('/', function(req, res) {
    res.render("upload", {title: "file upload!"});
  }); 
  
router.post("/", function(req, res, next){
      if (req.files) {
        //   console.log(util.inspect(req.files));
          if (req.files[0].size === 0) {
                return next(new Error("select a file?"));
          }
          console.log(req.files[0].path);
          fs.exists(req.files[0].path, function(exists) {
              if(exists) {
                  let sessId = req.session.id;
                  let db ={
                            sessId: sessId,
                            path : req.files[0].path
                          };
                  
                  let data = JSON.stringify(db);
                  fs.writeFileSync('../data/data.json',data);
		  console.log("entering the arrow conversion stage");
                  convertToArrow(sessId, function(res){
                    console.log("arrow file conversion complete");
                  });        
                  res.redirect('../calc');
              } else {
                  res.end("oh snap, that didn't work!");
              }
          });
      }else{
        res.send("fail");
      }
  });
  
  function convertToArrow(sessId,callback){
    var spawn = require('child_process').spawn;  
    var py = spawn('python3', ['../python-scripts/convertToArrow.py', sessId]);
    py.stdin.write(JSON.stringify(sessId));
    py.stdout.on('end', function(){
      callback("success");
    });
    py.stdin.end();
    
  }
  module.exports = router;

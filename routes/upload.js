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
                  let db = {
                    path : req.files[0].path
                  }
                  let data = JSON.stringify(db);
                  fs.writeFileSync('data/data.json',data);        
                  res.send("ok");

                  // callPy(req.files[0].path, function(val){
                  //   console.log(val);
                  // });
                  
              } else {
                  res.end("oh snap, that didn't work!");
              }
          });
      }else{
        res.send("fail");
      }
  });

  
  module.exports = router;
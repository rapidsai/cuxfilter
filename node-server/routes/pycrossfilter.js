var express = require('express');
var router = express.Router();
// var util = require("util");
// var fs = require("fs"); 
var spawn = require('child_process').spawn;
var net = require('net');
var HOST = '127.0.0.1';
var PORT = 3001;
var startTime, endTime;
var pyClient;
var tryAgain = 0;
var isConnectionEstablished = false;
var isDataLoaded = false;
var dataLoaded = '';

module.exports = function(io) {

    //SOCKET.IO

    io.on('connection',function(socket){

        //initialize the socket connection with the python script. this is executed when user initializes a pycrossfilter instance
        socket.on('init', function(callback){
            if(isConnectionEstablished){
                callback(false,'connection already established');
            }else{
                initConnection(function(error,result){
                    console.log(result);
                    callback(error, result);
                });
            }
        });

        //loads the data in GPU memory
        socket.on('load_data', function(file, callback){
            
            console.log("user tried to load data from "+file);

            if(isDataLoaded && dataLoaded === file){
                console.log('data already loaded');
                callback(false,'data already loaded');
            }else{
                loadData(file, function(result){
                    callback(false, result);
                });
            }
        });
    
        //get size of the dataset
        socket.on('size', function(callback){
            console.log("user requesting size of the dataset");
            getSize(function(result){
                callback(false,result);
            });
        });

        //getHist
        socket.on('getHist', function(name, callback){
            console.log("user requested histogram for "+name);
            getHist(name, function(result){
                var response = {
                    pyData: Buffer.from(result).toString('utf8'),
                    nodeServerTime: Date.now() - startTime
                }
                console.log(response);
                callback(false,JSON.stringify(response));
            });
        });
    });


    return router;
};

function initConnection(callback){
    var pyServer = spawn('python3', ['../python-scripts/pycrossfilter.py']);
    pyClient = new net.Socket();
    pyClient.connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    });
    pyClient.on('error',function(err){
        console.log("failed. Trying again... ");
        if(tryAgain === 0){
            setTimeout(function(){
              pyClient.connect(PORT, HOST, function() {
              });
           },1000);
           tryAgain=1;
         }else{
            callback(true,"something went wrong, try connection again");
        }

    });
    pyClient.on('connect', function(){
        isConnectionEstablished = true;
        callback(false,'user has connected to pycrossfilter');
    });
}


function loadData(file, callback){
    pyClient.on('data', function(val){
        console.log("received data from pyscript");
        var response = {
            pyData: Buffer.from(val).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        console.log(response);
        isDataLoaded = true;
        dataLoaded = file;
        callback(JSON.stringify(response));
    });

    pyClient.write('read:::'+file);
}

function getSize(callback){
    pyClient.on("data", function(size){
        callback(Buffer.from(size).toString('utf8'));
    });
    pyClient.write("size");
}

function getHist(columnName,callback){
    pyClient.on("data", function(cols){
        callback(cols);
    });
    pyClient.write("hist:::10:::numba:::"+columnName);
}

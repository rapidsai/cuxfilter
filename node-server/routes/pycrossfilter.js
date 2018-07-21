var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn;
var net = require('net');
var HOST = '127.0.0.1';
var PORT = 3001;
var startTime, endTime;
var pyClient = {};//, pyServer = {};
var pyServer;
var tryAgain = 0;
var isConnectionEstablished = {};
var isDataLoaded = false;
var dataLoaded = '';

module.exports = function(io) {

    //SOCKET.IO

    io.on('connection',function(socket){

        //initialize the socket connection with the python script. this is executed when user initializes a pycrossfilter instance
        socket.on('init', function(num_connections,callback){
            console.log(socket.id);
            if(isConnectionEstablished[socket.id]){
                callback(false,'connection already established');
            }else{
                initConnection(num_connections,socket.id,function(error,result){
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
                callback(true,'data already loaded');
            }else{
                loadData(file,socket.id, function(result){
                    callback(false, result);
                });
            }
        });
    
        //get size of the dataset
        socket.on('size', function(callback){
            console.log("getsize"+socket.id);
            console.log("user requesting size of the dataset");
            getSize(socket.id,function(result){
                callback(false,result);
            });
        });

        //getHist
        socket.on('getHist', function(name,bins, callback){
            console.log("user requested histogram for "+name);
            getHist(name,bins,socket.id, function(result){
                var response = {
                    pyData: Buffer.from(result).toString('utf8'),
                    nodeServerTime: Date.now() - startTime
                }
                console.log(response);
                callback(false,JSON.stringify(response));
            });
        });

        //onClose
        socket.on('disconnect', function () {
            pyClient[socket.id].destroy();
        });
    });


    return router;
};

function initConnection(num_connections,socket_id,callback){
    pyServer = spawn('python3', ['../python-scripts/pycrossfilter.py',num_connections]);
    pyServer.stdout.on('data', function(data) {
        console.log('PyServer stdout ');
        //Here is where the output goes
    });
    pyClient[socket_id] = new net.Socket();
    pyClient[socket_id].connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    });
    pyClient[socket_id].on('error',function(err){
        console.log("failed. Trying again... ");
        if(tryAgain === 0){
            setTimeout(function(){
              pyClient[socket_id].connect(PORT, HOST, function() {
              });
           },1000);
           tryAgain=1;
         }else{
            callback(true,"something went wrong, try connection again");
        }

    });
    pyClient[socket_id].on('connect', function(){
        isConnectionEstablished = true;
        callback(false,'user has connected to pycrossfilter');
    });
}


function loadData(file,socket_id, callback){
    pyClient[socket_id].on('data', function(val){
        console.log("received data from pyscript");
        var response = {
            pyData: Buffer.from(val).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        console.log(response);
        isDataLoaded = true;
        dataLoaded = file;
        pyClient[socket_id].removeAllListeners(['data']);
        callback(JSON.stringify(response));
    });

    pyClient[socket_id].write('read:::'+file);
}

function getSize(socket_id,callback){
    pyClient[socket_id].on("data", function(size){
        pyClient[socket_id].removeAllListeners(['data']);
        callback(Buffer.from(size).toString('utf8'));
    });
    pyClient[socket_id].write("size");
}

function getHist(columnName,bins,socket_id,callback){
    pyClient[socket_id].on("data", function(cols){
        pyClient[socket_id].removeAllListeners(['data']);
        callback(cols);
    });
    pyClient[socket_id].write("hist:::10:::numba:::"+columnName+":::"+bins);
}

var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn;
var net = require('net');
var HOST = '127.0.0.1';
var PORT = 3001;
var startTime, endTime;
var pyClient = {};//, pyServer = {};
var pyServer = {};
var tryAgain = 0;
var isConnectionEstablished = {}; // key -> session_id; value: socket.id
var isDataLoaded = {};
var dataLoaded = {};
var session_id = '';

module.exports = function(io) {

    //SOCKET.IO

    router.get('/', function(req, res) {
        var sessId = req.session.id;   
        console.log("session id is : "+sessId);
        session_id = sessId;
        res.end("ok");
    }); 


    io.on('connection',function(socket){

        //initialize the socket connection with the python script. this is executed when user initializes a pycrossfilter instance
        socket.on('init', function(file, callback){
            if(isConnectionEstablished[session_id+file] === true){
                callback(false,'connection already established');
            }else{
                initConnection(session_id,socket.id,file,function(error,result){
                    // console.log(result);
                    callback(error, result);
                });
            }
        });

        //loads the data in GPU memory
        socket.on('load_data', function(file, callback){
            
            console.log("user tried to load data from "+file);

            if(isDataLoaded[session_id+file] && dataLoaded[session_id+file] === file){
                console.log('data already loaded');
                callback(true,'data already loaded');
            }else{
                loadData(file,session_id, function(result){
                    callback(false, result);
                });
            }
        });
    
        //get size of the dataset
        socket.on('size', function(file,callback){
            console.log("user requesting size of the dataset");
            getSize(session_id,file,function(result){
                callback(false,result);
            });
        });

        //getHist
        socket.on('getHist', function(name,bins,file, callback){
            console.log(session_id);
            console.log("user requested histogram for "+name);
            getHist(name,bins,session_id,file, function(result){
                var response = {
                    pyData: Buffer.from(result).toString('utf8'),
                    nodeServerTime: Date.now() - startTime
                }
                //console.log(response);
                callback(false,JSON.stringify(response));
            });
        });

        // socket.on('disconnect', function(){

        // });
        //onClose
        socket.on('endSession', function (file,callback) {
            pyClient[session_id+file].destroy();
            isDataLoaded[session_id+file] = false;
            isConnectionEstablished[session_id+file] = false;
            callback(false,"session ended");
        });
    });


    return router;
};

// function numClients(session_id){
//     for(var key in clients){

//     }
// }


function initConnection(session_id,socket_id,file, callback){
    var server_file = file.split(":::")[0];
    var server_key = session_id+server_file;
    var threadCount = 'threadCount';
    if(!(server_key in pyServer) || (server_key in pyServer && pyServer[threadCount+server_key]>3)){
        pyServer[threadCount+server_key] = 1;
        pyServer[server_key] = spawn('python3', ['../python-scripts/pycrossfilter.py',3]);
        pyServer[server_key].stdout.on('data', function(data) {
            console.log('PyServer stdout ');
            //Here is where the output goes
        });
    }else{
        pyServer[threadCount+server_key]= pyServer[threadCount+server_key] + 1;
    }
    
    pyClient[session_id+file] = new net.Socket();
    pyClient[session_id+file].connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    });
    pyClient[session_id+file].on('error',function(err){
        console.log("failed. Trying again... ");
        if(tryAgain === 0){
            setTimeout(function(){
              pyClient[session_id+file].connect(PORT, HOST, function() {
              });
           },1000);
           tryAgain=1;
         }else{
            callback(true,"something went wrong, try connection again");
        }

    });
    pyClient[session_id+file].on('connect', function(){
        isConnectionEstablished[session_id+file] = true;
        callback(false,'user has connected to pycrossfilter');
    });
}


function loadData(file,session_id, callback){
    pyClient[session_id+file].on('data', function(val){
        console.log("received data from pyscript");
        var response = {
            pyData: Buffer.from(val).toString('utf8'),
            nodeServerTime: Date.now() - startTime
        }
        console.log(response);
        isDataLoaded[session_id+file] = true;
        dataLoaded[session_id+file] = file;
        pyClient[session_id+file].removeAllListeners(['data']);
        callback(JSON.stringify(response));
    });

    pyClient[session_id+file].write('read:::'+file);
}

function getSize(session_id,file,callback){
    pyClient[session_id+file].on("data", function(size){
        pyClient[session_id+file].removeAllListeners(['data']);
        callback(Buffer.from(size).toString('utf8'));
    });
    pyClient[session_id+file].write("size");
}

function getHist(columnName,bins,session_id,file,callback){
    pyClient[session_id+file].on("data", function(cols){
        pyClient[session_id+file].removeAllListeners(['data']);
        callback(cols);
    });
    pyClient[session_id+file].write("hist:::10:::numba:::"+columnName+":::"+bins);
}

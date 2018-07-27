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
                initConnection(session_id,file,function(error,result){
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
                console.log("loading new data in gpu mem");
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

        //get top/bottom n rows as per the top n values of columnName
        socket.on('filter_Order', function(sortOrder, name,file,n,callback){
            console.log("user has requested top n rows as per the column "+name);
            if(isConnectionEstablished[session_id+file]){
                getFilteredOrdered(sortOrder,name,file,n,session_id, function(result){
                    var response = {
                        pyData: Buffer.from(result).toString('utf8'),
                        nodeServerTime: Date.now() - startTime
                    }
                    //console.log(response);
                    callback(false,JSON.stringify(response));
                });
            }else{
                var response = {
                    pyData: 'No connection established',
                    nodeServerTime: Date.now() - startTime
                }
                callback(false,JSON.stringify(response));
            }
        });

        //getHist
        socket.on('getHist', function(name,file,bins, callback){
            console.log(session_id);
            console.log("user requested histogram for "+name);
            if(isConnectionEstablished[session_id+file]){
                getHist(name,file,bins,session_id, function(result){
                    var response = {
                        pyData: Buffer.from(result).toString('utf8'),
                        nodeServerTime: Date.now() - startTime
                    }
                    //console.log(response);
                    callback(false,JSON.stringify(response));
                });
            }else{
                var response = {
                    pyData: 'No connection established',
                    nodeServerTime: Date.now() - startTime
                }
                callback(false,JSON.stringify(response));
            }
            
        });

        //get Max and Min for a dimension
        socket.on('getMaxMin', function(columnName,file,callback){
            console.log("user requested max-min values for "+columnName);
            getMaxMin(columnName,file, function(result){
                callback(false, Buffer.from(result).toString('utf8'));
            });
        });


        // socket.on('disconnect', function(){
        // });
        //onClose
        socket.on('endSession', function (file,callback) {

            for(var key in pyClient){
                if(key.includes(session_id+file)){
                    pyClient[key].write("exit");
                    pyClient[key].destroy();
                    isDataLoaded[key] = false;
                    isConnectionEstablished[key] = false;
                }
            }
            callback(false,"session ended");
        });
    });


    return router;
};

// function numClients(session_id){
//     for(var key in clients){

//     }
// }


function initConnection(session_id,file, callback){
    var server_file = file.split(":::")[0];
    var server_key = session_id+server_file;
    var threadCount = 'threadCount';
    console.log("server key"+server_key);
    if(!(server_key in pyServer) || (server_key in pyServer && pyServer[threadCount+server_key]>3)){
        pyServer[threadCount+server_key] = 1;
        pyServer[server_key] = spawn('python3', ['../python-scripts/pycrossfilter.py',3]);
        console.log("server successfully spawned");
        pyServer[server_key].stdout.on('data', function(data) {
            console.log('PyServer stdout ');
            console.log(Buffer.from(data).toString('utf8'));
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
    console.log('inside loaddata');
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

function getHist(columnName,file,bins,session_id,callback){
    pyClient[session_id+file].on("data", function(cols){
        pyClient[session_id+file].removeAllListeners(['data']);
        callback(cols);
    });
    pyClient[session_id+file].write("hist:::"+session_id+":::numba:::"+columnName+":::"+bins);
}


function getFilteredOrdered(sortOrder, columnName,file,n,session_id,callback){
    pyClient[session_id+file].on("data", function(data){
        pyClient[session_id+file].removeAllListeners(['data']);
        callback(data);
    });
    pyClient[session_id+file].write("filterOrder:::"+sortOrder+":::"+session_id+":::numba:::"+columnName+":::"+n);
}


function getMaxMin(columnName, file, callback){
    pyClient[session_id+file].on("data", function(data){
        pyClient[session_id+file].removeAllListeners(['data']);
        console.log("max-min"+data);
        callback(data);
    });
    pyClient[session_id+file].write("get_max_min:::"+session_id+":::"+columnName);
}

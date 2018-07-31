var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn;
var net = require('net');
var HOST = '127.0.0.1';
var PORT = 3001;
var startTime, endTime;
var pyClient = {};
var pyServer = {};
var tryAgain = 0;
var isConnectionEstablished = {}; // key -> session_id; value: socket.id
var isDataLoaded = {};
var dataLoaded = {};
var serverOnTime = {};
// var session = require('express-session');

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
        socket.on('init', function(dataset, callback){
            try{
                console.log("connection init requested");
                socket.session_id = parseCookie(socket.handshake.headers.cookie);
                if(isConnectionEstablished[socket.session_id+dataset] === true){
                    callback(false,'connection already established');
                }else{
                    initConnection(socket.session_id,dataset,function(error,result){
                        callback(error, result);
                    });
                }
            }catch(ex){
                console.log(ex);
                clearGPUMem();
            }
        });

        //loads the data in GPU memory
        socket.on('load_data', function(dataset, callback){
            try{
                console.log("user tried to load data from "+dataset);
                resetServerTime(dataset,socket.session_id);
                if(isDataLoaded[socket.session_id+dataset] && dataLoaded[socket.session_id+dataset] === dataset){
                    console.log('data already loaded');
                    callback(true,'data already loaded');
                }else{
                    console.log("loading new data in gpu mem");
                    loadData(dataset,socket.session_id, function(result){
                        callback(false, result);
                    });
                }
            }catch(ex){
                console.log(ex);
                clearGPUMem();
            }
        });

        //get schema of the dataset
        socket.on('getSchema', function(dataset,callback){
            try{
                console.log("user requesting schema of the dataset");
                process_client_input(socket.session_id,dataset, 'schema', function(error,message){
                    if(!error){
                        console.log("schema: "+message);
                        callback(error,message);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }

        });
    
        
        //query the dataframe -> return results
        socket.on('filter', function(columnName,dataset,comparison,value,callback){
            try{
                console.log("user requesting filtering of the dataset");
                var query_args = ["filter",columnName,comparison,value];
                process_client_input(socket.session_id,dataset, create_query(query_args), function(error,message){
                    if(!error){
                        callback(error,message);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //reset all filters on a dimension
        socket.on('filterAll', function(dataset, callback){
            try{
                console.log("user requesting resetting filters on the current dimension");
                var query_args = ["reset",dataset];
                console.log("query:"+create_query(query_args));
                process_client_input(socket.session_id,dataset, create_query(query_args), function(error,message){
                    if(!error){
                        callback(error,message);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //get size of the dataset
        socket.on('size', function(dataset,callback){
            try{
                console.log("user requesting size of the dataset");
                process_client_input(socket.session_id,dataset, 'size', function(error,message){
                    if(!error){
                        console.log("size: "+message);
                        callback(error,message);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //get top/bottom n rows as per the top n values of columnName
        socket.on('filterOrder', function(sortOrder, columnName,dataset,n,callback){
            try{
                console.log("user has requested top n rows as per the column "+columnName);
                var query_args = ["filterOrder",sortOrder,columnName,n];

                process_client_input(socket.session_id,dataset, create_query(query_args), function(error,message){
                    if(!error){
                        callback(error,message);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //getHist
        socket.on('getHist', function(name,dataset,bins, callback){
            try{
                console.log("user requested histogram for "+name);
                var query_args = ["hist",name,bins];
                process_client_input(socket.session_id,dataset, create_query(query_args), function(error,message){
                    if(!error){
                        callback(error,message);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
            
        });

        //get Max and Min for a dimension
        socket.on('getMaxMin', function(columnName,dataset,callback){
            try{
                console.log("user requested max-min values for "+columnName+" for data="+dataset);
                var query_args = ['get_max_min',columnName];
                process_client_input(socket.session_id,dataset, create_query(query_args), function(error,message){
                    if(!error){
                        callback(error,message);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });


        socket.on('disconnect', function(){
        });
        //onClose
        socket.on('endSession', function (dataset,callback) {
            try{
                for(var key in pyClient){
                    if(key.includes(socket.session_id+dataset)){
                        pyClient[key].write("exit");
                        pyClient[key].destroy();
                        isDataLoaded[key] = false;
                        isConnectionEstablished[key] = false;
                    }
                }
                callback(false,"session ended");

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });
    });

    return router;
};


//Utility functions:
function parseCookie(cookie){
    var output = {};
    cookie.split(/\s*;\s*/).forEach(function(pair) {
        pair = pair.split(/\s*=\s*/);
        output[pair[0]] = pair.splice(1).join('=');
    });
    return output['connect.sid'].toString('utf8').split('.')[0].substring(4);
}

setInterval(function(){
    console.log("clearing the clutter");
    console.log(Object.keys(serverOnTime));
    for(var key in serverOnTime){
        if(Date.now() - serverOnTime[key] > 10*60*1000){
            console.log("clearing "+key);
            pyClient[key].write("exit");
            pyClient[key].destroy();
            isDataLoaded[key] = false;
            isConnectionEstablished[key] = false;
        }
    }
},10*59*1000);

function clearGPUMem(){
    console.log(Object.keys(serverOnTime));
    console.log(Object.keys(pyClient));

    for(var key in serverOnTime){
        console.log("clearing "+key);

            pyClient[key].write("exit");
            pyClient[key].destroy();
            isDataLoaded[key] = false;
            isConnectionEstablished[key] = false;
    }
}

function process_client_input(session_id, dataset, query,callback){
    try{
        resetServerTime(dataset,session_id);
        if(isConnectionEstablished[session_id+dataset]){
            utils(session_id,dataset, query,function(result){
                var pyresponse = Buffer.from(result).toString('utf8').split(":::");
                var response = {
                    data: pyresponse[0],
                    pythonScriptTime: pyresponse[1],
                    nodeServerTime: Date.now() - startTime
                }
                callback(false,JSON.stringify(response));
            });
        }else{
            var response = {
                data: 'No connection established',
                pythonScriptTime: 0,
                nodeServerTime: Date.now() - startTime
            }
            callback(false,JSON.stringify(response));
        }
    }catch(ex){
        console.log(ex);
        callback(true,-1);
        clearGPUMem();
    }
}

function resetServerTime(dataset, session_id){
    var server_dataset = dataset.split(":::")[0];
    var server_key = session_id+server_dataset;
    serverOnTime[server_key] = Date.now();
}

function create_query(list_of_args){
    if(list_of_args instanceof Array){
        if(list_of_args.length ==0){
            return "number of arguments cannot be zero";
        }
        query = list_of_args[0];
        for(var index=1; index<list_of_args.length; index++){
            if(index == list_of_args.length-1){
                query = query + ":::" +list_of_args[index] + "///";
            }else{
                query = query + ":::" +list_of_args[index]
            }
        }
        return query;
    }else{
        return "input has to be an array of arguments";
    }
    
}
function initConnection(session_id,dataset, callback){
    var server_dataset = dataset.split(":::")[0];
    var server_key = session_id+server_dataset;
    var threadCount = 'threadCount';
    console.log("server key"+server_key);
    if(!(server_key in pyServer) || (server_key in pyServer && pyServer[threadCount+server_key]>1)){
        pyServer[threadCount+server_key] = 1;
        pyServer[server_key] = spawn('python3', ['../python-scripts/pycrossfilter.py',1]);
        console.log("server successfully spawned");
        pyServer[server_key].stdout.on('data', function(data) {
            console.log('PyServer stdout ');
            console.log(Buffer.from(data).toString('utf8'));
            //Here is where the output goes
        });
    }else{
        pyServer[threadCount+server_key]= pyServer[threadCount+server_key] + 1;
    }
    
    pyClient[session_id+dataset] = new net.Socket();
    pyClient[session_id+dataset].connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    });
    pyClient[session_id+dataset].on('error',function(err){
        console.log("failed. Trying again... ");
        if(tryAgain === 0){
            setTimeout(function(){
              pyClient[session_id+dataset].connect(PORT, HOST, function() {
              });
           },1000);
           tryAgain=1;
         }else{
            callback(true,"something went wrong, try connection again");
        }

    });
    pyClient[session_id+dataset].on('connect', function(){
        isConnectionEstablished[session_id+dataset] = true;
        callback(false,'user has connected to pycrossfilter');
    });
}


function loadData(dataset,session_id, callback){
    try{
        console.log('inside loaddata');
        pyClient[session_id+dataset].on('data', function(val){
            console.log("received data from pyscript");
            var pyresponse = Buffer.from(val).toString('utf8').split(":::");
            var response = {
                data: pyresponse[0],
                pythonScriptTime: pyresponse[1],
                nodeServerTime: Date.now() - startTime
            }
            console.log(response);
            isDataLoaded[session_id+dataset] = true;
            dataLoaded[session_id+dataset] = dataset;
            pyClient[session_id+dataset].removeAllListeners(['data']);
            callback(JSON.stringify(response));
        });
        var temp = create_query(['read',dataset]);
        console.log(temp);
        pyClient[session_id+dataset].write(temp);
    }catch(ex){
        console.log(ex);
        clearGPUMem();
    }
    
}


function utils(session_id,dataset, query,callback){
    try{
        pyClient[session_id+dataset].on("data", function(result){
            pyClient[session_id+dataset].removeAllListeners(['data']);
            callback(Buffer.from(result).toString('utf8'));
        });
        pyClient[session_id+dataset].write(query);
    }catch(ex){
        console.log(ex);
        clearGPUMem();
    }
}
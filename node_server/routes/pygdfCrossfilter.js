const express = require('express');
const router = express.Router();
const spawn = require('child_process').spawn;
const net = require('net');
const HOST = '127.0.0.1';
const PORT = 3001;
const pyClient = {};
const pyServer = {};
const isConnectionEstablished = {}; // key -> session_id; value: socket.id
const isDataLoaded = {};
const dataLoaded = {};
const serverOnTime = {};
// var session = require('express-session');
const callback_store = {};
const startTimeStore = {};
let chunks = [];
const got = require('got');
const pyServerURL = 'http://127.0.0.1:3002';

module.exports = function(io) {

    //SOCKET.IO
    router.get('/', function(req, res) {
        var sessId = req.session.id;
        console.log("session id is : "+sessId);
        session_id = sessId;
        res.end("ok");
    });

    io.on('connection',function(socket){

        //initialize the socket connection with the python script. this is executed when user initializes a pygdfCrossfilter instance
        socket.on('init', function(dataset, engine, callback){
            try{
                console.log("connection init requested");
                socket.session_id = parseCookie(socket.handshake.headers.cookie);
                if(isConnectionEstablished[socket.session_id+dataset+engine] === true){
                    callback(false,'connection already established');
                }else{
                    // let query = {
                    //     'session_id': socket.session_id,
                    //     'dataset': dataset,
                    //     'engine': engine
                    // };
                    initConnection(socket.session_id,dataset, engine, function(error,result){
                        callback(error, result);
                    });
                }
            }catch(ex){
                console.log(ex);
                clearGPUMem();
            }
        });

        //loads the data in GPU memory
        socket.on('load_data', function(dataset,engine, callback){
            try{
                console.log("user tried to load data from "+dataset);
                // resetServerTime(dataset,socket.session_id);

                if(isDataLoaded[socket.session_id+dataset+engine] && dataLoaded[socket.session_id+dataset+engine] === dataset && isConnectionEstablished[socket.session_id+dataset+engine]){
                      console.log('data already loaded');
                      let startTime = Date.now();
                      let command = 'reset_all_filters';
                      let query = {
                          'session_id': socket.session_id,
                          'dataset': dataset,
                          'engine': engine
                      };

                      pygdf_query(command,params(query),'reset_all', engine);

                      //send data already loaded custom response
                      var response = {
                                    data: 'data already loaded',
                                    pythonScriptTime: 0,
                                    nodeServerTime: (Date.now() - startTime)/1000
                                };
                      callback(false, JSON.stringify(response));
                }else{

                      console.log("loading new data in gpu mem");
                      let command = 'read_data';
                      let query = {
                          'session_id': socket.session_id,
                          'dataset': dataset,
                          'engine': engine
                      };
                      console.log("params",params(query));

                      pygdf_query(command,params(query),'read_data',engine,(error, message) => {
                          if(!error){
                            isDataLoaded[socket.session_id+dataset+engine] = true
                            dataLoaded[socket.session_id+dataset+engine] = dataset
                            callback(false,message);
                          }else{
                            console.log(error);
                            callback(true, error);
                          }
                      });
                    }
            }catch(ex){
                console.log(ex);
                clearGPUMem();
            }
        });

        socket.on("resetAllFilters", function(dataset,engine,callback){
            let command = 'reset_all_filters';
            let query = {
                'session_id': socket.session_id,
                'dataset': dataset,
                'engine': engine
            };

            pygdf_query(command,params(query),'reset_all',engine,callback);
        });

        //get schema of the dataset
        socket.on('getSchema', function(dataset,engine,callback){
            try{
                let command = 'get_schema';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting schema of the dataset",engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }

        });

        //load dimension
        socket.on('dimension_load', function(column_name,dataset,engine, callback){
            try{
                let command = 'dimension_load';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting loading a new dimension:"+column_name,engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //query the dataframe -> return results
        socket.on('dimension_filter', function(column_name,dataset,comparison,value,engine,callback){
            try{
                let command = 'dimension_filter';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'comparison_operation':comparison,
                    'value': value,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting filtering of the dataset",engine,(error, message) => {
                    if(!error){
                      socket.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                      callback(false,message);
                    }else{
                      console.log(error);
                      callback(true,error);
                    }
                });

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //query the dataframe -> return results
        socket.on('groupby_load', function(column_name,dataset,agg,engine,callback){
            try{
                let command = 'groupby_load';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'groupby_agg':agg,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting groupby for the dimension:"+column_name,engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //get top/bottom n rows as per the top n values of columnName
        socket.on('groupby_filterOrder', function(sort_order, column_name,dataset,n,sort_column,agg,engine,callback){
            try{

                let command = 'groupby_filterOrder';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'groupby_agg':agg,
                    'sort_order': sort_order,
                    'num_rows': n,
                    'sort_column': sort_column,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user has requested filterOrder rows for the groupby operation for dimension:"+column_name,engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

         //query the dataframe as per a range-> return results
         socket.on('dimension_filter_range', function(column_name,dataset,range_min,range_max,engine,callback){
            try{
                let command = 'dimension_filter_range';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'min_value':range_min,
                    'max_value': range_max,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting filtering of the dataset as per a range of rows",engine,(error, message) => {
                    if(!error){
                      socket.emit("update_size", dataset, JSON.parse(message)['data']);
                      callback(false,message);
                    }else{
                      console.log(error);
                      callback(true,error);
                    }
                });

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //reset all filters on a dimension
        socket.on('dimension_filterAll', function(column_name,dataset,engine, callback){
            try{
                let command = 'dimension_reset';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting resetting filters on the current dimension",engine,(error, message) => {
                    if(!error){
                      socket.emit("update_size", dataset, JSON.parse(message)['data']);
                      callback(false,message);
                    }else{
                      console.log(error);
                      callback(true,error);
                    }
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });


        socket.on('groupby_size', function(column_name,dataset,agg,engine, callback){
            try{
                let command = 'groupby_size';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'groupby_agg':agg,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting size of the groupby",engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //get size of the dataset
        socket.on('size', function(dataset,engine,callback){
            try{
                let command = 'get_size';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requesting size of the dataset",engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //get top/bottom n rows as per the top n values of columnName
        socket.on('dimension_filterOrder', function(sort_order, column_name, dataset, num_rows, columns,engine,callback){
            try{

                let command = 'dimension_filterOrder';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'sort_order': sort_order,
                    'num_rows': num_rows,
                    'columns': columns,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user has requested top n rows as per the column "+column_name,engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });

        //getHist
        socket.on('dimension_getHist', function(column_name,dataset,num_of_bins, engine,callback){
            try{
                let command = 'dimension_hist';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'num_of_bins': num_of_bins,
                    'engine': engine
                };

                pygdf_query(command,params(query),"user requested histogram for "+column_name,engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }

        });

        //get Max and Min for a dimension
        socket.on('dimension_getMaxMin', function(column_name,dataset,engine,callback){
            try{

                let command = 'dimension_get_max_min';
                let query = {
                    'session_id': socket.session_id,
                    'dataset': dataset,
                    'dimension_name': column_name,
                    'engine': engine
                };
                let comment = "user requested max-min values for "+column_name+" for data="+dataset;

                pygdf_query(command,params(query),comment,engine,callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                clearGPUMem();
            }
        });


        socket.on('disconnect', function(){
        });
        //onClose
        socket.on('endSession', function (dataset,engine,callback) {
            endSession(socket.session_id,dataset,engine, function(error, message){
                callback(error,message);
            });
        });
    });

    return router;
};


function callPyServer(command,query, engine){
  return new Promise((resolve, reject) => {
       let startTime = Date.now();
       let url = pyServerURL+'/'+command+'?'+query
       got(url)
        .then(val => {
          var pyresponse = Buffer.from(val.body).toString('utf8').split(":::");
          var response = {
                        data: pyresponse[0],
                        pythonScriptTime: parseFloat(pyresponse[1]),
                        nodeServerTime: ((Date.now() - startTime)/1000) - parseFloat(pyresponse[1])
                        }
          if(response.data == 'oom error, please reload'){
            isDataLoaded[session_id+dataset+engine] = false;
            isConnectionEstablished[session_id+dataset+engine] = false;
          }
          resolve(JSON.stringify(response));
        }).catch(error => {
          console.log(error);
          var response = {
                          data: error.toString(),
                          pythonScriptTime: parseFloat(0),
                          nodeServerTime: ((Date.now() - startTime)/1000)
                        }
          reject(true,JSON.stringify(response));
        });
  });
}

function params(data) {
  let dataset = data['dataset'];
  let session_id = data['session_id']
  let engine = data['engine']
  resetServerTime(dataset,session_id,engine);
  return Object.keys(data).map(key => `${key}=${encodeURIComponent(data[key])}`).join('&');
}

function pygdf_query(command,query, comments,engine, callback){
    callPyServer(command,query, engine)
      .then((message) => {
              console.log(comments);
              typeof callback === 'function' && callback(false,message);
      }).catch((error) => {
              console.log(error);
              typeof callback === 'function' && callback(error,false);
      });
}

function endSession(session_id,dataset,engine,callback){
  let startTime = Date.now()
  url = 'http://127.0.0.1:3002/end_connection?session_id='+session_id+'&dataset='+dataset+'&engine='+engine
  got(url)
   .then(val => {
     isDataLoaded[session_id+dataset+engine] = false;
     isConnectionEstablished[session_id+dataset+engine] = false;
     var pyresponse = Buffer.from(val.body).toString('utf8').split(":::");
     var response = {
                   data: pyresponse[0],
                   pythonScriptTime: parseFloat(pyresponse[1]),
                   nodeServerTime: ((Date.now() - startTime)/1000) - parseFloat(pyresponse[1])
               }
     callback(false,JSON.stringify(response));
   }).catch(error => {
     console.log(error);
     var response = {
                     data: error.toString(),
                     pythonScriptTime: parseFloat(0),
                     nodeServerTime: ((Date.now() - startTime)/1000)
                   }
     reject(true,JSON.stringify(response));
   });
}

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
            // pyClient[key].write("exit");
            // pyClient[key].destroy();
            endSession(key.split(':::')[0], key.split(':::')[1], key.split(':::')[2], (err,res) => {
              console.log(res);
            });
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

            // pyClient[key].write("exit");
            // pyClient[key].destroy();
            isDataLoaded[key] = false;
            isConnectionEstablished[key] = false;
    }
}

// function process_client_input(session_id, dataset, query){
//     return new Promise((resolve, reject) => {
//          let startTime = Date.now();
//          url = 'http://127.0.0.1:3002/process?session_id='+session_id+'&query='+query
//          got(url)
//           .then(val => {
//             var pyresponse = Buffer.from(val.body).toString('utf8').split(":::");
//             var response = {
//                           data: pyresponse[1],
//                           pythonScriptTime: pyresponse[2],
//                           nodeServerTime: ((Date.now() - startTime)/1000) - parseFloat(pyresponse[2])
//                       }
//             resolve(JSON.stringify(response));
//           }).catch(error => {
//             console.log(error);
//             reject(true,error.toString());
//           });
//     });
// }

function resetServerTime(dataset, session_id, engine){
  console.log(dataset);
  console.log(session_id);
    var server_dataset = dataset.split(":::")[0];
    var server_key = session_id+":::"+server_dataset+":::"+engine;
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
                query = query + ":::" +list_of_args[index];
            }else{
                query = query + ":::" +list_of_args[index]
            }
        }
        return query;
    }else{
        return "input has to be an array of arguments";
    }

}
function initConnection(session_id,dataset,engine, callback){
    let startTime = Date.now()
    // let url = pyServerURL+'/'+'init_connection'+'?'+query
    let url = 'http://127.0.0.1:3002/init_connection?session_id='+session_id+'&engine='+engine+'&dataset='+dataset;
    got(url)
      .then(val => {
        console.log(val.body)
        isConnectionEstablished[session_id+dataset+engine] = true
        var pyresponse = Buffer.from(val.body).toString('utf8').split(":::");
        var response = {
                      data: pyresponse[0],
                      pythonScriptTime: parseFloat(pyresponse[1]),
                      nodeServerTime: ((Date.now() - startTime)/1000) - parseFloat(pyresponse[1])
                  }
        callback(false,JSON.stringify(response));
      }).catch(error => {
        console.log(error);
        isConnectionEstablished[session_id+dataset+engine] = false;
        var response = {
                        data: error.toString(),
                        pythonScriptTime: parseFloat(0),
                        nodeServerTime: ((Date.now() - startTime)/1000)
                      }
        callback(true,JSON.stringify(response));
      });
}

//Utility functions:
const config = require('/usr/src/app/config.json');
const isConnectionEstablished = {}; // key -> session_id; value: socket.id
const isDataLoaded = {};
const dataLoaded = {};
const serverOnTime = {};

const pyServerURLPygdf = config.flask_server_url+":"+config.flask_server_port_pygdf
const pyServerURLPandas = config.flask_server_url+":"+config.flask_server_port_pandas
let singleSessionId = {
  'pygdf': '',
  'pandas': ''
};
const sessionlessID = 111;
const got = require('got');


//init connection and set session_id
function init_session(socket, dataset, engine, usingSessions, cookies){
  if(usingSessions){
      let tempSessionId = parseCookie(cookies);
      if(tempSessionId != singleSessionId[engine]){
          endSession(singleSessionId[engine],dataset,engine,(error, message) =>{
              if(!error){
                singleSessionId[engine] = tempSessionId;
                console.log("old session replaced with new session, gpu mem cleared");
              }else{
                singleSessionId[engine] = tempSessionId;
                console.log("old session replaced with new session, failed:",message);
              }
          });
        }
      return tempSessionId;
  }else{
      return utils.sessionlessID;
  }
}




//triggering an update event which broadcasts to all the neighbouring socket connections in case of a multi-tab sessionless access
function triggerUpdateEvent(socket, dataset, engine){
  console.log("broadcasting update");
  socket.emit("update_event", dataset,engine);
  socket.broadcast.emit("update_event", dataset,engine);
}

//calling the python server(pandas or pygdf) with the command and query
function callPyServer(command,query, engine){
  return new Promise((resolve, reject) => {
       let startTime = Date.now();
       let url = pyServerURLPygdf+'/'+command+'?'+query
       if(engine == 'pandas'){
         url = pyServerURLPandas+'/'+command+'?'+query
       }
       got(url)
        .then(val => {
          var pyresponse = Buffer.from(val.body).toString('utf8').split(":::");
          var response = {
                        data: pyresponse[0],
                        pythonScriptTime: parseFloat(pyresponse[1]),
                        nodeServerTime: ((Date.now() - startTime)/1000) - parseFloat(pyresponse[1]),
                        activeFilters: pyresponse[2]
                        }
          if(response.data.indexOf('Exception') > -1){
            response.data = response.data.split('***')[1];
            if(response.data.indexOf('out of memory') > -1  || response.data.indexOf('thrust::system::system_error') > -1){
              isDataLoaded[session_id+dataset+engine] = false;
              isConnectionEstablished[session_id+dataset+engine] = false;
              // endSession(session_id,dataset,engine,(err,message)=>{});
            }
            reject(JSON.stringify(response));
          }else{
            resolve(JSON.stringify(response));
          }

        }).catch(error => {
          console.log(error);
          var response = {
                          data: error.toString(),
                          pythonScriptTime: parseFloat(0),
                          nodeServerTime: ((Date.now() - startTime)/1000)
                        }
          reject(JSON.stringify(response));
        });
  });
}

//convert json object to encodeURIComponent
function params(data, session_id, dataset, engine) {
  // let dataset = data['dataset'];
  // let session_id = data['session_id']
  // let engine = data['engine']
  // resetServerTime(dataset,session_id,engine);
  data['session_id'] = session_id;
  data['dataset'] = dataset;
  data['engine'] = engine;
  return Object.keys(data).map(key => `${key}=${encodeURIComponent(data[key])}`).join('&');
}

//handle queries by calling the python server and returning the results directly to the socket-io-client on the front-end
function pygdf_query(command,query, comments,engine, callback){
    callPyServer(command,query, engine)
      .then((message) => {
              console.log(comments);
              // socket.broadcast.emit(command,false,message);
              typeof callback === 'function' && callback(false,message);
      }).catch((error_message) => {
              console.log(error_message);
              typeof callback === 'function' && callback(true,error_message);
      });
}

//end session and remove the dataframe from the gpu memory
function endSession(session_id,dataset,engine,callback){
  let startTime = Date.now()
  let url = pyServerURLPygdf+'/end_connection?session_id='+session_id+'&dataset='+dataset+'&engine='+engine
  if(engine == 'pandas'){
    url = pyServerURLPandas+'/end_connection?session_id='+session_id+'&dataset='+dataset+'&engine='+engine
  }

  got(url)
   .then(val => {
     console.log("session is being ended");
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
     callback(true,JSON.stringify(response));
   });
}


//parse a cookie received from the browser and return object
function parseCookie(cookie){
    var output = {};
    cookie.split(/\s*;\s*/).forEach(function(pair) {
        pair = pair.split(/\s*=\s*/);
        output[pair[0]] = pair.splice(1).join('=');
    });
    return output['connect.sid'].toString('utf8').split('.')[0].substring(4);
}

//clear gpu memory
function clearGPUMem(){
    console.log(Object.keys(serverOnTime));

    for(var key in serverOnTime){
        console.log("clearing "+key);
            isDataLoaded[key] = false;
            isConnectionEstablished[key] = false;
    }
};

//reset last active time for a session
function resetServerTime(dataset, session_id, engine){
  console.log(dataset);
  console.log(session_id);
    var server_dataset = dataset.split(":::")[0];
    var server_key = session_id+":::"+server_dataset+":::"+engine;
    serverOnTime[server_key] = Date.now();
}

//create a query object from a array of arguments
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

//initialize connection with pyServer by creating a pygdf/pandas object
function initConnection(session_id,dataset,engine, callback){
    let startTime = Date.now()
    // let url = pyServerURL+'/'+'init_connection'+'?'+query
    let url = pyServerURLPygdf+'/init_connection?session_id='+session_id+'&engine='+engine+'&dataset='+dataset
    if(engine == 'pandas'){
      url = pyServerURLPandas+'/init_connection?session_id='+session_id+'&engine='+engine+'&dataset='+dataset
    }
    got(url)
      .then(val => {
        console.log(val.body)
        isConnectionEstablished[session_id+dataset+engine] = true
        var pyresponse = Buffer.from(val.body).toString('utf8').split(":::");
        var response = {
                      data: pyresponse[0],
                      pythonScriptTime: parseFloat(pyresponse[1]),
                      nodeServerTime: ((Date.now() - startTime)/1000) - parseFloat(pyresponse[1]),
                      activeFilters: pyresponse[2]
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


module.exports = {

  isConnectionEstablished: isConnectionEstablished,
  isDataLoaded: isDataLoaded,
  dataLoaded: dataLoaded,
  serverOnTime: serverOnTime,
  pyServerURLPygdf: pyServerURLPygdf,
  pyServerURLPandas: pyServerURLPandas,
  singleSessionId: singleSessionId,
  sessionlessID: sessionlessID,

  //init connection and set session_id
  init_session: init_session,

  //triggering an update event which broadcasts to all the neighbouring socket connections in case of a multi-tab sessionless access
  triggerUpdateEvent: triggerUpdateEvent,

  //calling the python server(pandas or pygdf) with the command and query
  callPyServer: callPyServer,

  //convert json object to encodeURIComponent
  params: params,

  //handle queries by calling the python server and returning the results directly to the socket-io-client on the front-end
  pygdf_query: pygdf_query,

  //end session and remove the dataframe from the gpu memory
  endSession: endSession,

  //Utility functions:

  //parse a cookie received from the browser and return object
  parseCookie: parseCookie,

  //clear gpu memory
  clearGPUMem: clearGPUMem,

  //reset last active time for a session
  resetServerTime: resetServerTime,

  //create a query object from a array of arguments
  create_query: create_query,

  //initialize connection with pyServer by creating a pygdf/pandas object
  initConnection: initConnection

}

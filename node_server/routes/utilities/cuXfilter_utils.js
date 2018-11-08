//Utility functions:
const config = require('/usr/src/app/config.json');
const isConnectionEstablished = {}; // key -> session_id; value: socket.id
const isDataLoaded = {};
const dataLoaded = {};
const serverOnTime = {};

const pyServerURLcudf = config.flask_server_url+":"+config.flask_server_port_cudf
const pyServerURLPandas = config.flask_server_url+":"+config.flask_server_port_pandas
let singleSessionId = {
  'cudf': '',
  'pandas': ''
};
const sessionlessID = 111;
const got = require('got');

const dimensions = {};
const histograms = {};
const groups = {};

//init connection and set session_id
function initSession(socket, dataset, engine, usingSessions, cookies){
  resetParams();
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
      return sessionlessID;
  }
}

function resetParams(){
  Object.keys(dimensions).forEach(function (prop) {
    delete dimensions[prop];
  });
  Object.keys(histograms).forEach(function (prop) {
    delete histograms[prop];
  });
  Object.keys(groups).forEach(function (prop) {
    delete groups[prop];
  });
}


function updateClientSideSize(socket,dataset,engine, dataset_size){
  // console.log('inside updateClientSideSize');
  socket.emit("update_size", dataset,engine, dataset_size);
  if(socket.useSessions == false){
    console.log('broadcasting size');
    socket.broadcast.emit("update_size", dataset,engine, dataset_size);
  }
}

function updateClientSideDimensions(socket, dataset, engine, dimension_name,startTime){
  return new Promise((resolve,reject) => {
    let length_groups = Object.keys(dimensions).length;
    let i = 0;
    if(i == length_groups){
      resolve();
    }
    for(let dimension in dimensions){
      if(dimensions.hasOwnProperty(dimension)){// && dimension.indexOf(dimension_name) < 0){
        i = i+1;
        let command = 'dimension_filter_order';
        let query = dimensions[dimension];
        cudf_query(command,params(query, socket.session_id, dataset, engine),"user has requested "+query.sort_order+" n rows as per the column "+query.dimension_name, engine, startTime, (error, message)=>{
          if(!error){
            socket.emit('update_dimension', query.dimension_name, engine, message);
            if(socket.useSessions == false){
              console.log('broadcasting dimension');
              socket.broadcast.emit('update_dimension', query.dimension_name, message);
            }
            console.log('dimensions',i);
            if(i == length_groups){
              resolve();
            }
          }else{
            console.log('error in updateClientSideDimensions:');
            console.log(message);
          }
        });
      }
    }
  });
}

function updateClientSideHistograms(socket, dataset, engine, dimension_name,startTime){
  return new Promise((resolve,reject) => {
      let length_groups = Object.keys(histograms).length;
      let i = 0;
      if(i == length_groups){
        resolve();
      }
      for(let histogram in histograms){
        if(histograms.hasOwnProperty(histogram)){ //&& histogram.indexOf(dimension_name) < 0){
          i = i+1;
          let command = 'dimension_hist';
          let query = histograms[histogram];
          cudf_query(command,params(query, socket.session_id, dataset, engine),"user requested histogram for "+query.dimension_name, engine,startTime, (error, message)=>{
            if(!error){
              socket.emit('update_hist', query.dimension_name, engine, message);
              if(socket.useSessions == false){
                console.log('broadcasting histogram');
                socket.broadcast.emit('update_hist', query.dimension_name, message);
              }
              console.log('histograms',i,Object.keys(histograms).length);
              if(i == length_groups){
                resolve();
              }
            }else{
              console.log('error in updateClientSideHistograms:');
              console.log(message);
            }
          });
        }
      }
    });
}

function updateClientSideGroups(socket, dataset, engine, dimension_name,startTime){
  return new Promise((resolve,reject) => {
    let length_groups = Object.keys(groups).length;
    let i = 0;
    if(i == length_groups){
      resolve();
    }
    for(let group in groups){
        if(groups.hasOwnProperty(group)){// && group.indexOf(dimension_name) < 0){
          i = i+1;
          let command = 'groupby_filter_order';
          let query = groups[group];
          // console.log("query for group",query);
          cudf_query(command,params(query, socket.session_id, dataset, engine),"updating filter_order for group:"+query.dimension_name, engine,startTime, (error, message)=>{
            if(!error){
              socket.emit('update_group', query.dimension_name, query.groupby_agg, engine, message);
              if(socket.useSessions == false){
                console.log('broadcasting group');
                socket.broadcast.emit('update_group', query.dimension_name, query.groupby_agg, engine, message);
              }
              console.log('groups',i);
              if(i == length_groups){
                resolve();
              }
            }else{
              console.log('error in updateClientSideGroups:');
              console.log(message);
            }
          });
        }
      }
    });
}
//triggering an update event which broadcasts to all the neighbouring socket connections in case of a multi-tab sessionless access
function updateClientSideValues(socket, dataset, engine, dataset_size, startTime, dimension_name='null'){
  // let startTime = Date.now();
  updateClientSideSize(socket,dataset,engine,dataset_size);
  Promise.all([updateClientSideDimensions(socket, dataset, engine, dimension_name,startTime),
              updateClientSideHistograms(socket, dataset, engine, dimension_name,startTime),
              updateClientSideGroups(socket, dataset, engine, dimension_name,startTime)])
              .then(()=> {
                console.log('all updates complete');
                socket.emit('all_updates_complete', dataset, engine);
                if(socket.useSessions == false){
                  socket.broadcast.emit('all_updates_complete', dataset, engine);
                }
              });
}


function groupbyMessageCustomParse(message){
  let temp_message = JSON.parse(message);
  temp_message['size'] = temp_message['data'].split('&')[1];
  temp_message['data'] = temp_message['data'].split('&')[0];
  console.log(temp_message['size']);
  return JSON.stringify(temp_message);
}

//calling the python server(pandas or cudf) with the command and query
function callPyServer(command,query, engine, startTime){
  return new Promise((resolve, reject) => {
       // let startTime = Date.now();
       let url = pyServerURLcudf+'/'+command+'?'+query
       if(engine == 'pandas'){
         url = pyServerURLPandas+'/'+command+'?'+query
       }
       got(url)
        .then(val => {
          var pyresponse = Buffer.from(val.body).toString('utf8').split("&");
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
  data['session_id'] = session_id;
  data['dataset'] = dataset;
  data['engine'] = engine;
  return Object.keys(data).map(key => `${key}=${encodeURIComponent(data[key])}`).join('&');
}

//handle queries by calling the python server and returning the results directly to the socket-io-client on the front-end
function cudf_query(command,query, comments, engine, startTime, callback){
    callPyServer(command,query, engine, startTime)
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
  let url = pyServerURLcudf+'/end_connection?session_id='+session_id+'&dataset='+dataset+'&engine='+engine
  if(engine == 'pandas'){
    url = pyServerURLPandas+'/end_connection?session_id='+session_id+'&dataset='+dataset+'&engine='+engine
  }

  got(url)
   .then(val => {
     console.log("session is being ended");
     isDataLoaded[session_id+dataset+engine] = false;
     isConnectionEstablished[session_id+dataset+engine] = false;
     var pyresponse = Buffer.from(val.body).toString('utf8').split("&");
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
    var server_dataset = dataset.split("&")[0];
    var server_key = session_id+"&"+server_dataset+"&"+engine;
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
                query = query + "&" +list_of_args[index];
            }else{
                query = query + "&" +list_of_args[index]
            }
        }
        return query;
    }else{
        return "input has to be an array of arguments";
    }

}

//initialize connection with pyServer by creating a cudf/pandas object
function initConnection(session_id,dataset,engine, callback){
    let startTime = Date.now()
    // let url = pyServerURL+'/'+'init_connection'+'?'+query
    let url = pyServerURLcudf+'/init_connection?session_id='+session_id+'&engine='+engine+'&dataset='+dataset
    if(engine == 'pandas'){
      url = pyServerURLPandas+'/init_connection?session_id='+session_id+'&engine='+engine+'&dataset='+dataset
    }
    got(url)
      .then(val => {
        console.log(val.body)
        isConnectionEstablished[session_id+dataset+engine] = true
        var pyresponse = Buffer.from(val.body).toString('utf8').split("&");
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
  pyServerURLcudf: pyServerURLcudf,
  pyServerURLPandas: pyServerURLPandas,
  singleSessionId: singleSessionId,
  sessionlessID: sessionlessID,

  dimensions: dimensions,
  groups: groups,
  histograms: histograms,
  //init connection and set session_id
  initSession: initSession,

  //triggering an update event which broadcasts to all the neighbouring socket connections in case of a multi-tab sessionless access
  // triggerUpdateEvent: triggerUpdateEvent,

  //calling the python server(pandas or cudf) with the command and query
  callPyServer: callPyServer,

  //convert json object to encodeURIComponent
  params: params,

  //handle queries by calling the python server and returning the results directly to the socket-io-client on the front-end
  cudf_query: cudf_query,

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

  //initialize connection with pyServer by creating a cudf/pandas object
  initConnection: initConnection,

  updateClientSideSize: updateClientSideSize,
  updateClientSideDimensions:updateClientSideDimensions,
  updateClientSideHistograms:updateClientSideHistograms,
  updateClientSideGroups:updateClientSideGroups,
  updateClientSideValues: updateClientSideValues,

  groupbyMessageCustomParse: groupbyMessageCustomParse
}

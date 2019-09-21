//Utility functions:
// const config = require('/usr/src/app/config.json');
let currentConnection = {}; // key -> session_id+":::"+dataset+":::"+engine; value: true/false
let currentDataLoaded = {}; // key -> session_id+":::"+dataset+":::"+engine; value: true/false
const serverOnTime = {};

const pyServerURLcudf = "http://localhost:"+process.env.sanic_server_port_cudf
const pyServerURLPandas = "http://localhost:"+process.env.sanic_server_port_pandas

const sessionlessID = 111;
const got = require('got');

const dimensions = {};
const histograms = {};
const groups = {};

//init connection and set session_id
function initSession(io, socket, dataset, engine, usingSessions, cookies){
  if(usingSessions){
      let tempSessionId = parseCookie(cookies);
      clearGPUMem(io, tempSessionId);

      let temp_key = tempSessionId+":::"+dataset+":::"+engine;
      //
      if(currentConnection.hasOwnProperty(temp_key) && currentConnection[temp_key] == false){
          resetParams(tempSessionId, dataset, engine);
      }
      return tempSessionId;
  }else{
      // resetParams(sessionlessID, dataset, engine);
      return sessionlessID;
  }
}

function resetParams(session_id, dataset, engine){
  //reset_all_filters
  // if(clear_filters){
  //   cudf_query('reset_all_filters',params({}, session_id, dataset, engine),'reset_all',engine, Date.now(), session_id+":::"+dataset+":::"+engine);
  // }
  const key = session_id+":::"+dataset+":::"+engine;
  if(key in dimensions){
    Object.keys(dimensions[key]).forEach(function (prop) {
      delete dimensions[key][prop];
    });
  }
  if(key in histograms){
    Object.keys(histograms[key]).forEach(function (prop) {
      delete histograms[key][prop];
    });
  }

  if(key in groups){
    Object.keys(groups[key]).forEach(function (prop) {
      delete groups[key][prop];
    });
  }

}


function updateClientSideSize(io, socket,dataset,engine, dataset_size){
  io.to(socket.session_id).emit("update_size", dataset,engine, dataset_size);
}

function updateClientSideDimensions(io, socket, dataset, engine, dimension_name,startTime){
  console.log('updating dimensions started');
  return new Promise((resolve,reject) => {
    const key = socket.session_id+":::"+dataset+":::"+engine;
    if(!(key in dimensions)){
      resolve();
    }
    else{
        let length_dimensions = Object.keys(dimensions[key]).length;
        let i = 0;
        if(i === length_dimensions){
          console.log('updating dimensions ended');
          resolve();
        }else{
          for(let dimension in dimensions[key]){
            if(dimensions[key].hasOwnProperty(dimension)){// && dimension.indexOf(dimension_name) < 0){
              i = i+1;
              let command = 'dimension_filter_order';
              let query = dimensions[key][dimension];
              cudf_query(command,params(query, socket.session_id, dataset, engine),"user has requested "+query.sort_order+" n rows as per the column "+query.dimension_name, engine, startTime, socket.session_id+":::"+dataset+":::"+engine, (error, message)=>{
                if(!error){
                  io.to(socket.session_id).emit('update_dimension', dataset, engine, query.dimension_name, message);
                  // console.log('dimensions',i);
                  if(i == length_dimensions){
                    // console.log('updating dimensions ended');
                    resolve();
                  }
                }else{
                  console.log('error in updateClientSideDimensions:');
                  console.log(message);
                  reject();
                }
              });
            }
          }
          // console.log('something went wrong in updateClientSideDimensions', dimensions, key);
          // reject();
        }
    }
  });
}

function updateClientSideHistograms(io, socket, dataset, engine, dimension_name,startTime){
  console.log('updating hist started');
  return new Promise((resolve,reject) => {
      const key = socket.session_id+":::"+dataset+":::"+engine;
      if(!(key in histograms)){
        resolve();
      }
      else{
          let length_histograms = Object.keys(histograms[key]).length;
          let i = 0;
          if(i == length_histograms){
            console.log('updating hist ended');
            resolve();
          }else{
            console.log('in update histograms', histograms[key])
            for(let histogram in histograms[key]){
              if(histograms[key].hasOwnProperty(histogram)){ //&& histogram.indexOf(dimension_name) < 0){
                i = i+1;
                let command = 'dimension_hist';
                let query = histograms[key][histogram];
                console.log(query);
                cudf_query(command,params(query, socket.session_id, dataset, engine),"user requested histogram for "+query.dimension_name, engine,startTime,socket.session_id+":::"+dataset+":::"+engine, (error, message)=>{
                  if(!error){
                    console.log('updating hist', i);
                    io.to(socket.session_id).emit('update_hist', dataset, engine, query.dimension_name, message);
                    if(i == length_histograms){
                      console.log('updating hist ended');
                      resolve();
                    }
                  }else{
                    console.log('error in updateClientSideHistograms:');
                    console.log(message);
                    reject();
                  }
                });
              }
            }
            // console.log('something went wrong in updateClientSideHistograms', i,length_histograms,Object.keys(histograms[key]).length);
            // reject();
          }
      }
    });
}

function updateClientSideGroups(io, socket, dataset, engine, dimension_name,startTime){
  console.log('updating groups started');
  return new Promise((resolve,reject) => {
    const key = socket.session_id+":::"+dataset+":::"+engine;
    if(!(key in groups)){
      resolve();
    }
    else{
        let length_groups = Object.keys(groups[key]).length;
        let i = 0;
        if(i == length_groups){
          console.log('updating groups ended');
          resolve();
        }else{
          for(let group in groups[key]){
              if(groups[key].hasOwnProperty(group)){// && group.indexOf(dimension_name) < 0){
                i = i+1;
                let command = 'groupby_filter_order';
                let query = groups[key][group];
                // console.log("query for group",query);
                cudf_query(command,params(query, socket.session_id, dataset, engine),"updating filter_order for group:"+query.dimension_name, engine,startTime,socket.session_id+":::"+dataset+":::"+engine, (error, message)=>{
                  if(!error){
                    io.to(socket.session_id).emit('update_group', dataset, engine, query.dimension_name, query.groupby_agg, message);

                    // console.log('groups',i);
                    if(i == length_groups){
                      // console.log('updating groups ended');
                      resolve();
                    }
                  }else{
                    console.log('error in updateClientSideGroups:');
                    console.log(message);
                    reject();
                  }
                });
              }
            }
           // console.log('something went wrong in updateClientSideGroups');
           // reject();
        }

    }

    });
}
//triggering an update event which broadcasts to all the neighbouring socket connections in case of a multi-tab sessionless access
function updateClientSideValues(io, socket, dataset, engine, dataset_size, startTime, dimension_name='null'){
  // let startTime = Date.now();
  updateClientSideSize(io, socket,dataset,engine,dataset_size);
  console.log('update all started');
  Promise.all([updateClientSideDimensions(io, socket, dataset, engine, dimension_name,startTime),
              updateClientSideHistograms(io, socket, dataset, engine, dimension_name,startTime),
              updateClientSideGroups(io, socket, dataset, engine, dimension_name,startTime)])
              .then(()=> {
                console.log('all updates complete');
                io.to(socket.session_id).emit('all_updates_complete', dataset, engine);
              })
              .catch(() => {
                console.log('clientSideUpdate failed');
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
function callPyServer(command, query, engine, startTime, currentConnection_key){
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
              currentConnection[currentConnection_key] = false;
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
function cudf_query(command, query, comments, engine, startTime, currentConnection_key, callback){
    callPyServer(command, query, engine, startTime, currentConnection_key)
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
function endConnection(session_id,dataset,engine,callback){
  resetParams(session_id,dataset,engine);
  let startTime = Date.now()
  let url = pyServerURLcudf+'/end_connection?session_id='+session_id+'&dataset='+dataset+'&engine='+engine
  if(engine == 'pandas'){
    url = pyServerURLPandas+'/end_connection?session_id='+session_id+'&dataset='+dataset+'&engine='+engine
  }

  got(url)
   .then(val => {
     console.log("session is being ended");
     currentConnection[session_id+":::"+dataset+":::"+engine] = false;
     var pyresponse = Buffer.from(val.body).toString('utf8').split("&");
     var response = {
                   data: pyresponse[0],
                   pythonScriptTime: parseFloat(pyresponse[1]),
                   nodeServerTime: ((Date.now() - startTime)/1000) - parseFloat(pyresponse[1])
               }
     typeof callback === 'function' && callback(false,JSON.stringify(response));
   }).catch(error => {
     console.log(error);
     var response = {
                     data: error.toString(),
                     pythonScriptTime: parseFloat(0),
                     nodeServerTime: ((Date.now() - startTime)/1000)
                   }
     typeof callback === 'function' && callback(true,JSON.stringify(response));
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
function clearGPUMem(io, omit_session=''){
  //clear gpu memory for a particular session, by ending all dataset+engine connections using the endConnection function
    Object.keys(currentConnection).map((key) => {
      if(currentConnection[key] == true){
        let current_session_id = key.split(":::")[0];
        if(current_session_id !== omit_session){
          currentConnection[key] = false;
          let dataset = key.split(":::")[1];
          let engine = key.split(":::")[2];
          let message = 'your session has ended(and dataframe kicked of GPU Memory), as someone else established a new session(only one session allowed per container)';
          io.to(current_session_id).emit('session_ended',dataset, engine, message);
          endConnection(current_session_id,dataset,engine);
        }
      }
    });
};

//reset last active time for a session
function resetServerTime(dataset, session_id, engine){
  console.log(dataset);
  console.log(session_id);
    var server_dataset = dataset.split("&")[0];
    var server_key = session_id+engine;
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
function initConnection(session_id, dataset, engine, callback){
  console.log('inside initConnection', session_id, dataset, engine)
    let startTime = Date.now()
    // let url = pyServerURL+'/'+'init_connection'+'?'+query
    let url = pyServerURLcudf+'/init_connection?session_id='+session_id+'&engine='+engine+'&dataset='+dataset;
    if(engine == 'pandas'){
      url = pyServerURLPandas+'/init_connection?session_id='+session_id+'&engine='+engine+'&dataset='+dataset;
    }
    got(url)
      .then(val => {
        currentConnection[session_id+":::"+dataset+":::"+engine] = true;
        currentDataLoaded[session_id+":::"+dataset+":::"+engine] = false; //data not loaded yet
        console.log('successful init', currentConnection);
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
        currentConnection[session_id+":::"+dataset+":::"+engine] = false;
        currentDataLoaded[session_id+":::"+dataset+":::"+engine] = false; //data not loaded yet
        var response = {
                        data: error.toString(),
                        pythonScriptTime: parseFloat(0),
                        nodeServerTime: ((Date.now() - startTime)/1000)
                      }
        callback(true,JSON.stringify(response));
      });
}


module.exports = {

  currentConnection: currentConnection,
  currentDataLoaded: currentDataLoaded,
  serverOnTime: serverOnTime,
  pyServerURLcudf: pyServerURLcudf,
  pyServerURLPandas: pyServerURLPandas,
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
  endConnection: endConnection,

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

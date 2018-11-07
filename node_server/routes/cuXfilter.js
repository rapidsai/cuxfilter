const express = require('express');
const utils = require('./utilities/cuXfilter_utils');
const router = express.Router();

module.exports = (io) => {
    router.get('/', (req, res) => {
        res.end("ok");
    });

    //SOCKET.IO
    io.on('connection',(socket) => {

        //initialize the socket connection with the python script. this is executed when user initializes a cuXfilter instance
        socket.on('init', (dataset, engine, usingSessions, callback) => {
            try{
                  console.log("connection init requested");
                  socket.session_id = utils.initSession(socket, dataset, engine, usingSessions, socket.handshake.headers.cookie)
                  socket.useSessions = usingSessions;

                  if(utils.isConnectionEstablished[socket.session_id+dataset+engine] === true){
                      typeof callback === 'function' && callback(false,'connection already established');
                  }else{
                      utils.initConnection(socket.session_id,dataset, engine,callback);
                  }
            }catch(ex){
                console.log(ex);
                utils.clearGPUMem();
            }
        });

        //loads the data in GPU memory
        socket.on('load_data', (dataset,engine, load_type, callback) => {
            try{
                console.log("user tried to load data from "+dataset);

                if(utils.isDataLoaded[socket.session_id+dataset+engine] && utils.dataLoaded[socket.session_id+dataset+engine] == dataset){
                      console.log('data already loaded');
                      let startTime = Date.now();

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
                          'load_type': load_type
                      };

                      utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),'read_data',engine,Date.now(), (error, message) => {
                          if(!error){
                            utils.isDataLoaded[socket.session_id+dataset+engine] = true
                            utils.dataLoaded[socket.session_id+dataset+engine] = dataset
                          }
                          typeof callback === 'function' && callback(error, message);
                      });
                    }
            }catch(ex){
                console.log(ex);
                utils.clearGPUMem();
            }
        });

        //remove all filters from the dataset and retain the original dataset state
        socket.on("reset_all_filters", (dataset,engine,callback) => {
            let command = 'reset_all_filters';
            let query = {};
            let startTime = Date.now();
            utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),'reset_all',engine, startTime,  (error, message) => {
                if(!error){
                  let dataset_size = JSON.parse(message)['data'];
                  utils.updateClientSideValues(socket, dataset, engine, dataset_size,startTime);
                }
                typeof callback === 'function' && callback(error, message);
            });
        });

        //get schema of the dataset
        socket.on('get_schema', (dataset,engine,callback) => {
            try{
                let command = 'get_schema';
                let query = {};

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting schema of the dataset",engine,Date.now(),  callback);

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }

        });

        //load dimension
        socket.on('dimension_load', (dimension_name,dataset,engine, callback) => {
            try{
                let command = 'dimension_load';
                let query = {
                    'dimension_name': dimension_name
                };

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting loading a new dimension:"+dimension_name, engine,Date.now(),  callback);

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //query the dataframe -> return results
        socket.on('dimension_filter', (dimension_name,dataset,comparison,value,engine,pre_reset,callback) => {
            try{
                let command = 'dimension_filter';
                let query = {
                    'dimension_name': dimension_name,
                    'comparison_operation':comparison,
                    'value': value,
                    'pre_reset': pre_reset
                };
                let startTime = Date.now()
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting filtering of the dataset", engine, startTime,  (error, message) => {
                    if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideValues(socket, dataset, engine, dataset_size,startTime, dimension_name);
                    }
                    typeof callback === 'function' && callback(error, message);
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //query the dataframe -> return results
        socket.on('groupby_load', (dimension_name,dataset,agg,engine,callback) => {
            try{
                let command = 'groupby_load';
                let query = {
                    'dimension_name': dimension_name,
                    'groupby_agg':agg
                };

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting groupby for the dimension:"+dimension_name,engine,Date.now(),  (error,message) => {
                     callback(error,utils.groupbyMessageCustomParse(message));
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get top/bottom n rows as per the top n values of dimension_name
        socket.on('groupby_filter_order', (sort_order, dimension_name,dataset,n,sort_column,agg,engine,callback) => {
            try{

                let command = 'groupby_filter_order';
                let query = {
                    'dimension_name': dimension_name,
                    'groupby_agg':agg,
                    'sort_order': sort_order,
                    'num_rows': n,
                    'sort_column': sort_column
                };

                utils.groups[dimension_name+agg] = query;

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user has requested filter_order rows for the groupby operation for dimension:"+dimension_name, engine,Date.now(),  (error,message) => {
                  if(!error){
                    socket.emit('update_group', dimension_name, agg, engine, message);
                    if(socket.session_id === 111){
                      socket.broadcast.emit('update_group', dimension_name, agg, engine, message);
                    }
                  }else{
                    console.log('groupby filter order error',error);
                  }
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

         //query the dataframe as per a range-> return results
        socket.on('dimension_filter_range', (dimension_name, dataset, range_min, range_max, engine, pre_reset, callback) => {
            try{
                let command = 'dimension_filter_range';
                let query = {
                    'dimension_name': dimension_name,
                    'min_value':range_min,
                    'max_value': range_max,
                    'pre_reset': pre_reset
                };
                let startTime = Date.now();
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting filtering of the dataset as per a range of rows",engine, startTime, (error, message) => {
                    if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideValues(socket, dataset, engine, dataset_size, startTime, dimension_name);
                    }
                    typeof callback === 'function' && callback(error, message);
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //reset all filters on a dimension
        socket.on('dimension_reset_filters', (dimension_name,dataset,engine, callback) => {
            try{
                let command = 'dimension_reset';
                let query = {
                    'dimension_name': dimension_name
                };
                let startTime = Date.now();
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting resetting filters on the current dimension",engine, startTime, (error, message) => {
                    if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideValues(socket, dataset, engine, dataset_size,startTime, dimension_name);
                    }
                    typeof callback === 'function' && callback(error, message);
                });
            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get size of the current state of the dataset
        socket.on('size', (dataset,engine,callback) => {
            try{
                let command = 'get_size';
                let query = {};

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting size of the dataset",engine,Date.now(),  (error,message) => {
                  if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideSize(socket,dataset,engine, dataset_size);
                  }
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get top/bottom n rows as per the top n values of dimension_name
        socket.on('dimension_filter_order', (sort_order, dimension_name, dataset, num_rows, columns,engine,callback) => {
            try{

                let command = 'dimension_filter_order';
                let query = {
                    'dimension_name': dimension_name,
                    'sort_order': sort_order,
                    'num_rows': num_rows,
                    'columns': columns
                };
                utils.dimensions[dimension_name] = query;

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user has requested "+sort_order+" n rows as per the column "+dimension_name, engine,Date.now(),  (error,message) => {
                      if(!error){
                        socket.emit('update_dimension', dimension_name, engine, message);
                        if(socket.session_id === 111){
                          socket.broadcast.emit('update_dimension', dimension_name, engine, message);
                        }
                      }
                  });
            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get histogram specific to a column name in the given dataset, and as per the number of bins specified
        socket.on('dimension_get_hist', (dimension_name,dataset,num_of_bins, engine,callback) => {
            try{
                let command = 'dimension_hist';
                let query = {
                    'dimension_name': dimension_name,
                    'num_of_bins': num_of_bins
                };

                utils.histograms[dimension_name] = query;
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requested histogram for "+dimension_name, engine,Date.now(),  (error,message) => {
                  if(!error){
                    socket.emit('update_hist', dimension_name, engine, message);
                    if(socket.session_id === 111){
                      socket.broadcast.emit('update_hist', dimension_name, engine, message);
                    }
                  }
                });
            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }

        });

        //get Max and Min for a dimension
        socket.on('dimension_get_max_min', (dimension_name,dataset,engine,callback) => {
            try{

                let command = 'dimension_get_max_min';
                let query = {
                    'dimension_name': dimension_name
                };
                let comment = "user requested max-min values for "+dimension_name+" for data="+dataset;

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),comment,engine,Date.now(),  callback);

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //executes when socket connection disconnects
        socket.on('disconnect', () => {
        });

        //onClose
        socket.on('endSession', (dataset,engine,callback) => {
            utils.endSession(socket.session_id,dataset,engine, (error, message) => {
                typeof callback === 'function' && callback(error,message);
                if(socket.useSessions == false){
                  socket.broadcast.emit('session_ended', dataset, engine);
                }
            });
        });
    });

    return router;
};

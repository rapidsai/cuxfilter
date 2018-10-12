const express = require('express');
const utils = require('./utilities/pygdfCrossfilter_utils');
const router = express.Router();

module.exports = (io) => {
    router.get('/', (req, res) => {
        res.end("ok");
    });

    //SOCKET.IO
    io.on('connection',(socket) => {

        //initialize the socket connection with the python script. this is executed when user initializes a pygdfCrossfilter instance
        socket.on('init', (dataset, engine, usingSessions, callback) => {
            try{
                  console.log("connection init requested");
                  socket.session_id = utils.init_session(socket, dataset, engine, usingSessions, socket.handshake.headers.cookie)
                  socket.useSessions = usingSessions;

                  if(utils.isConnectionEstablished[socket.session_id+dataset+engine] === true){
                      callback(false,'connection already established');
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
                // utils.resetServerTime(dataset,socket.session_id);

                if(utils.isDataLoaded[socket.session_id+dataset+engine] && utils.dataLoaded[socket.session_id+dataset+engine] == dataset){
                      console.log('data already loaded');
                      let startTime = Date.now();

                      if(socket.useSessions == false){
                        socket.broadcast.emit("update_event", dataset,engine);
                      }
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
                          'load_type': load_type
                      };

                      utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),'read_data',engine, (error, message) => {
                          if(!error){
                            utils.isDataLoaded[socket.session_id+dataset+engine] = true
                            utils.dataLoaded[socket.session_id+dataset+engine] = dataset
                          }
                          callback(error, message);
                      });
                    }
            }catch(ex){
                console.log(ex);
                utils.clearGPUMem();
            }
        });

        //remove all filters from the dataset and retain the original dataset state
        socket.on("resetAllFilters", (dataset,engine,callback) => {
            let command = 'reset_all_filters';
            let query = {};

            utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),'reset_all',engine, (error, message) => {
                if(!error){
                  socket.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                  if(socket.useSessions == false){
                    socket.broadcast.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                    utils.triggerUpdateEvent(socket, dataset, engine);
                  }
                }
                callback(error, message);
            });
        });

        //get schema of the dataset
        socket.on('getSchema', (dataset,engine,callback) => {
            try{
                let command = 'get_schema';
                let query = {};

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting schema of the dataset",engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }

        });

        //load dimension
        socket.on('dimension_load', (column_name,dataset,engine, callback) => {
            try{
                let command = 'dimension_load';
                let query = {
                    'dimension_name': column_name
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting loading a new dimension:"+column_name, engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //query the dataframe -> return results
        socket.on('dimension_filter', (column_name,dataset,comparison,value,engine,callback) => {
            try{
                let command = 'dimension_filter';
                let query = {
                    'dimension_name': column_name,
                    'comparison_operation':comparison,
                    'value': value
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting filtering of the dataset", engine, (error, message) => {
                    if(!error){
                      socket.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                      if(socket.useSessions == false){
                        socket.broadcast.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                        utils.triggerUpdateEvent(socket, dataset, engine);
                      }
                    }
                    callback(error, message);
                });

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //query the dataframe -> return results
        socket.on('groupby_load', (column_name,dataset,agg,engine,callback) => {
            try{
                let command = 'groupby_load';
                let query = {
                    'dimension_name': column_name,
                    'groupby_agg':agg
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting groupby for the dimension:"+column_name,engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get top/bottom n rows as per the top n values of columnName
        socket.on('groupby_filterOrder', (sort_order, column_name,dataset,n,sort_column,agg,engine,callback) => {
            try{

                let command = 'groupby_filterOrder';
                let query = {
                    'dimension_name': column_name,
                    'groupby_agg':agg,
                    'sort_order': sort_order,
                    'num_rows': n,
                    'sort_column': sort_column
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user has requested filterOrder rows for the groupby operation for dimension:"+column_name, engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

         //query the dataframe as per a range-> return results
        socket.on('dimension_filter_range', (column_name,dataset,range_min,range_max,engine,callback) => {
            try{
                let command = 'dimension_filter_range';
                let query = {
                    'dimension_name': column_name,
                    'min_value':range_min,
                    'max_value': range_max
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting filtering of the dataset as per a range of rows",engine, (error, message) => {
                    if(!error){
                      socket.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                      if(socket.useSessions == false){
                        socket.broadcast.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                        utils.triggerUpdateEvent(socket, dataset, engine);
                      }
                    }
                    callback(error, message);
                });

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //reset all filters on a dimension
        socket.on('dimension_filterAll', (column_name,dataset,engine, callback) => {
            try{
                let command = 'dimension_reset';
                let query = {
                    'dimension_name': column_name
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting resetting filters on the current dimension",engine, (error, message) => {
                    if(!error){
                      socket.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                      if(socket.useSessions == false){
                        socket.broadcast.emit("update_size", dataset,engine, JSON.parse(message)['data']);
                        utils.triggerUpdateEvent(socket, dataset, engine);
                      }
                    }
                    callback(error, message);
                });
            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get size of the groupby aggregation result for the specific agg function & column name
        socket.on('groupby_size', (column_name,dataset,agg,engine, callback) => {
            try{
                let command = 'groupby_size';
                let query = {
                    'dimension_name': column_name,
                    'groupby_agg':agg
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting size of the groupby",engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get size of the current state of the dataset
        socket.on('size', (dataset,engine,callback) => {
            try{
                let command = 'get_size';
                let query = {};

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting size of the dataset",engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get top/bottom n rows as per the top n values of columnName
        socket.on('dimension_filterOrder', (sort_order, column_name, dataset, num_rows, columns,engine,callback) => {
            try{

                let command = 'dimension_filterOrder';
                let query = {
                    'dimension_name': column_name,
                    'sort_order': sort_order,
                    'num_rows': num_rows,
                    'columns': columns
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user has requested top n rows as per the column "+column_name, engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //get histogram specific to a column name in the given dataset, and as per the number of bins specified
        socket.on('dimension_getHist', (column_name,dataset,num_of_bins, engine,callback) => {
            try{
                let command = 'dimension_hist';
                let query = {
                    'dimension_name': column_name,
                    'num_of_bins': num_of_bins
                };

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requested histogram for "+column_name, engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }

        });

        //get Max and Min for a dimension
        socket.on('dimension_getMaxMin', (column_name,dataset,engine,callback) => {
            try{

                let command = 'dimension_get_max_min';
                let query = {
                    'dimension_name': column_name
                };
                let comment = "user requested max-min values for "+column_name+" for data="+dataset;

                utils.pygdf_query(command,utils.params(query, socket.session_id, dataset, engine),comment,engine, callback);

            }catch(ex){
                console.log(ex);
                callback(true,-1);
                utils.clearGPUMem();
            }
        });

        //executes when socket connection disconnects
        socket.on('disconnect', () => {
        });

        //onClose
        socket.on('endSession', (dataset,engine,callback) => {
            utils.endSession(socket.session_id,dataset,engine, (error, message) => {
                callback(error,message);
            });
        });
    });

    return router;
};

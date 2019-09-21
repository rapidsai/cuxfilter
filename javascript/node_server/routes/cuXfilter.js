const express = require('express');
const utils = require('./utilities/cuXfilter_utils');
const router = express.Router();

module.exports = (io) => {
    router.get('/', (req, res) => {
        res.send("ok");
    });

    //SOCKET.IO
    io.on('connection',(socket) => {

        //initialize the socket connection with the python script. this is executed when user initializes a cuXfilter instance
        socket.on('init', (dataset, engine, usingSessions, callback) => {
            try{
                  console.log("connection init requested");
                  socket.useSessions = usingSessions;
                  socket.session_id = utils.initSession(io, socket, dataset, engine, usingSessions, socket.handshake.headers.cookie)
                  socket.join(socket.session_id);
                  if(utils.currentConnection[socket.session_id+":::"+dataset+":::"+engine] === true){
                     console.log('connection already established')
                     typeof callback === 'function' && callback(false,'connection already established');
                  }else{
                     utils.initConnection(socket.session_id, dataset, engine, callback);
                  }

            }catch(ex){
                console.log(ex);
                utils.clearGPUMem(io);
                io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
            }
        });

        //loads the data in GPU memory
        socket.on('load_data', (dataset, engine, load_type, callback) => {
            try{
                console.log("user tried to load data from "+dataset);

                if(utils.currentConnection[socket.session_id+":::"+dataset+":::"+engine] === true && utils.currentDataLoaded[socket.session_id+":::"+dataset+":::"+engine] === true){
                      console.log('data already loaded');
                      let startTime = Date.now();
                      var response = {
                                    data: 'data already loaded',
                                    pythonScriptTime: 0,
                                    nodeServerTime: (Date.now() - startTime)/1000
                                };

                      callback(false, JSON.stringify(response));
                }else{
                      utils.currentDataLoaded[socket.session_id+":::"+dataset+":::"+engine] = false
                      console.log("loading new data in gpu mem");
                      let command = 'read_data';
                      let query = {
                          'load_type': load_type
                      };

                      utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),'read_data',engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine, (error, message) => {
                          if(!error){
                            utils.currentDataLoaded[socket.session_id+":::"+dataset+":::"+engine] = true
                            console.log('loaded new data', utils.currentConnection[socket.session_id+":::"+dataset+":::"+engine]);
                          }
                          typeof callback === 'function' && callback(error, message);
                      });
                    }
            }catch(ex){
                console.log(ex);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user'); socket.broadcast.emit('session_ended', dataset, engine, 'session ended by user');
            }
        });

        //remove all filters from the dataset and retain the original dataset state
        socket.on("reset_all_filters", (dataset,engine,callback) => {
            let command = 'reset_all_filters';
            let query = {};
            let startTime = Date.now();
            utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),'reset_all',engine, Date.now(),socket.session_id+":::"+dataset+":::"+engine,  (error, message) => {
                if(!error){
                  let dataset_size = JSON.parse(message)['data'];
                  utils.updateClientSideValues(io, socket, dataset, engine, dataset_size,startTime);
                }
                typeof callback === 'function' && callback(error, message);
            });
        });

        //get schema of the dataset
        socket.on('get_schema', (dataset,engine,callback) => {
            try{
                let command = 'get_schema';
                let query = {};

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting schema of the dataset",engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  callback);

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
            }

        });

        //load dimension
        socket.on('dimension_load', (dimension_name,dataset,engine, callback) => {
            try{
                let command = 'dimension_load';
                let query = {
                    'dimension_name': dimension_name
                };
                utils.dimensions[socket.session_id+":::"+dataset+":::"+engine] = {};

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting loading a new dimension:"+dimension_name, engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  callback);

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting filtering of the dataset", engine, Date.now(), socket.session_id+":::"+dataset+":::"+engine,  (error, message) => {
                    if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideValues(io, socket, dataset, engine, dataset_size,startTime, dimension_name);
                    }
                    typeof callback === 'function' && callback(error, message);
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);
                io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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
                utils.groups[socket.session_id+":::"+dataset+":::"+engine] = {}
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting groupby for the dimension:"+dimension_name,engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  (error,message) => {
                     callback(error,message);
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);
                io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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
                const key = socket.session_id+":::"+dataset+":::"+engine;
                if(!(key in utils.groups)){
                  utils.groups[key] = {};
                }
                utils.groups[key][dimension_name+agg] = query;

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user has requested filter_order rows for the groupby operation for dimension:"+dimension_name, engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  (error,message) => {
                  if(!error){
                    io.to(socket.session_id).emit('update_group', dataset, engine, dimension_name, agg, message);
                  }else{
                    console.log('groupby filter order error',error);
                  }
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting filtering of the dataset as per a range of rows",engine, Date.now(),socket.session_id+":::"+dataset+":::"+engine, (error, message) => {
                    if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideValues(io, socket, dataset, engine, dataset_size, startTime, dimension_name);
                    }
                    typeof callback === 'function' && callback(error, message);
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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
                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting resetting filters on the current dimension",engine, Date.now(),socket.session_id+":::"+dataset+":::"+engine, (error, message) => {
                    if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideValues(io, socket, dataset, engine, dataset_size,startTime, dimension_name);
                    }
                    typeof callback === 'function' && callback(error, message);
                });
            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
            }
        });

        //get size of the current state of the dataset
        socket.on('size', (dataset,engine,callback) => {
            try{
                let command = 'get_size';
                let query = {};

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requesting size of the dataset",engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  (error,message) => {
                  if(!error){
                      let dataset_size = JSON.parse(message)['data'];
                      utils.updateClientSideSize(socket,dataset,engine, dataset_size);
                  }
                });

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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
                const key = socket.session_id+":::"+dataset+":::"+engine;
                if(!(key in utils.dimensions)){
                  utils.dimensions[key] = {};
                }
                utils.dimensions[key][dimension_name] = query;


                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user has requested "+sort_order+" n rows as per the column "+dimension_name, engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  (error,message) => {
                      if(!error){
                        io.to(socket.session_id).emit('update_dimension', dataset, engine, dimension_name, message);
                      }
                  });
            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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
                const key = socket.session_id+":::"+dataset+":::"+engine;
                if(!(key in utils.histograms)){
                  utils.histograms[key] = {};
                }
                utils.histograms[key][dimension_name] = query;

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),"user requested histogram for "+dimension_name, engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  (error,message) => {
                  if(!error){
                    // io.to(socket.session_id).emit('update_hist', dataset, engine, dimension_name, message);
                    socket.emit('update_hist', dataset, engine, dimension_name, message);
                  }
                });
            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);
                io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
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

                utils.cudf_query(command,utils.params(query, socket.session_id, dataset, engine),comment,engine,Date.now(),socket.session_id+":::"+dataset+":::"+engine,  callback);

            }catch(ex){
                console.log(ex);
                typeof callback === 'function' && callback(true,-1);
                utils.clearGPUMem(io);
                io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
            }
        });

        //executes when socket connection disconnects
        socket.on('disconnect', () => {
          socket.disconnect();
        });

        //onClose
        socket.on('endSession', (dataset,engine,callback) => {
            utils.endConnection(socket.session_id,dataset,engine, (error, message) => {
                io.to(socket.session_id).emit('session_ended', dataset, engine, 'session ended by user');
                typeof callback === 'function' && callback(error,message);
                socket.disconnect();
            });
        });
    });

    return router;
};

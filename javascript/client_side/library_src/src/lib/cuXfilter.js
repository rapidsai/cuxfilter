// import dependencies
import io from 'socket.io-client';
import { Dimension } from '../util/dimension';

//cuXfilter.js
export class cuXfilter{
    constructor(dataset, url, engine, useSessions = true, load_type='arrow'){
        this.dataset = dataset;
        this.url = url;
        this.connected = false;
        this.size = 0;
        this.schema = [];
        this.childDimension = {};
        this.engine = engine;
        this.useSessions = useSessions;
        this.load_type = load_type;
        this.updateEvent = new CustomEvent('updateEvent', {detail: 'some other tab made changes to dimensions/groupbys'});
    }
    init(callback){
        return new Promise((resolve,reject) => {
            fetch(this.url+"/cuXfilter?transport=polling",{
                method: 'GET',
                credentials: 'include'
            }).then(res => {
                this.socket = io(this.url,{
                    path: '/cuXfilter'
                });

                this.socket.on('connect',() => {
                    console.log("connected to server");
                    this.tryConnecting(1, function(res){
                        if(res === -1){
                            reject('check if server is running');
                        }else{
                            resolve(res);
                        }
                    });
                });

                this.socket.on('disconnect',() => {
                    this.connected = false;
                });

                this.initSocketListeners();
            });
        });
    }

    tryConnecting(numAttempts, callback){
        if(numAttempts<3){
            this.socket.emit('init',this.dataset,this.engine, this.useSessions, (error, message) => {
                if(error){
                    this.tryConnecting(numAttempts+1, (res) =>{
                        typeof callback === 'function' && callback(res);
                    });
                }else{
                    this.connected = true;
                    this.loadData( (res) =>{
                        typeof callback === 'function' && callback(res);
                    });

                }
            });
        }else{
            callback(-1);
            console.log("could not connect, check if server container is running and gdf environment is activated");
        }

    }

    initSocketListeners(){
        this.socket.on('update_size', (dataset,engine, size) => {
            if(this.dataset === dataset && this.engine === engine){
                this.size = parseInt(size);
                dispatchEvent(new CustomEvent('updateSizeEvent', {detail: {'dataset': dataset}}));
            }
        });

        this.socket.on('all_updates_complete', (dataset,engine) => {
            if(this.dataset === dataset && this.engine === engine){
                dispatchEvent(new CustomEvent('allUpdatesComplete', {detail: {'dataset': dataset}}));
            }
        });

        this.socket.on('session_ended', (dataset, engine, message) => {
            if(engine == this.engine && this.dataset === dataset){
                this.connected = false;
                console.log(message);
                dispatchEvent(new CustomEvent('connectionClosed', {detail:message}));
            }
        });

        this.socket.on('update_hist', (dataset, engine, dimension_name, message) => {
            if(engine == this.engine && this.dataset === dataset && dimension_name in this.childDimension){
                this.childDimension[dimension_name].histogram = JSON.parse(JSON.parse(message)['data']);
                // this.childDimension[dimension_name].updateMaxMin();
                dispatchEvent(new CustomEvent('updateHistEvent', {detail: {'column': dimension_name}}));
            }
        });

        this.socket.on('update_dimension', (dataset, engine, dimension_name, message) => {
            if(engine == this.engine && this.dataset === dataset && dimension_name in this.childDimension){
                this.childDimension[dimension_name].value = JSON.parse(JSON.parse(message)['data']);
                this.childDimension[dimension_name].updateMaxMin();
                dispatchEvent(new CustomEvent('updateDimensionEvent', {detail: {'column': dimension_name}}));
            }
        });

        this.socket.on('update_group', (dataset, engine, dimension_name, agg,  message) => {
            if(engine == this.engine && this.dataset === dataset && dimension_name in this.childDimension){
                this.childDimension[dimension_name].childGroup[dimension_name+agg].value = JSON.parse(JSON.parse(message)['data']);
                dispatchEvent(new CustomEvent('updateGroupEvent', {detail: {column:dimension_name, aggregate:JSON.parse(agg)}}));
            }
        });
    }


    //load data in gpu memory of the server, executed automatically on a successful init()
    loadData(callback){
        if(this.connected){
            let startTime = Date.now();
            this.socket.emit('load_data',this.dataset,this.engine, this.load_type, (error,message) => {
                message = JSON.parse(message)

                //init metadata for the current dataset
                this.initMetaData( (res) => {
                    message['browserTime'] = (Date.now() - startTime)/1000;
                    typeof callback === 'function' && callback(message);
                });
            });
        }else{
            callback("Not connected");
        }
    }

    initMetaData(callback){
        if(this.connected){
            this.getSize();
            this.getSchema((res) => {
                typeof callback === 'function' && callback(res);
            });
        }else{
            console.log("Not connected");
        }
    }

    getSchema(callback){
        if(this.connected){
            let startTime = Date.now();
            this.socket.emit('get_schema', this.dataset,this.engine, (error,message) => {
                message = JSON.parse(message);
                message['browserTime'] = (Date.now() - startTime)/1000;
                this.schema = message['data'].replace(/[\[\]']+/g,"").split(', ');
                message['data'] = 'successfully loaded schema';
                callback(message);
            });
        }else{
            console.log("Not connected");
        }
    }

    getSize(){
        if(this.connected){
            this.socket.emit('size',this.dataset,this.engine);
        }else{
            console.log("Not connected");
        }
    }

    isConnected(){
        return this.connected;
    }

    dimension(name,callback){
        this.childDimension[name] = new Dimension(name,this.dataset, this.socket, this.engine);
        return this.childDimension[name];
    }

    resetAllFilters(){
        this.socket.emit('reset_all_filters',this.dataset,this.engine);
    }
    endSession(){
        return new Promise((resolve,reject) => {
            let startTime = Date.now();
            this.socket.emit('endSession',this.dataset,this.engine, (error, message) => {
                if(error){
                    reject(error);
                }else{
                    message = JSON.parse(message);
                    message['browserTime'] = (Date.now() - startTime)/1000;
                    this.connected = false;
                    this.socket.emit('disconnect');
                    resolve(message);
                }
            });
        });
    }
}

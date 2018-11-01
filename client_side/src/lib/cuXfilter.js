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
            fetch(this.url+"/cuXfilter",{
                method: 'GET',
                credentials: 'include'
            }).then(res => {
                console.log("cuXfilter initialized");

                this.socket = io(this.url,{
                    path: '/cuXfilter'
                });

                this.socket.on('connect',() => {
                    console.log("connected to server");
                    // console.log(this.socket.id);
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
            console.log(this);
            if(this.dataset === dataset && this.engine === engine){
                this.size = parseInt(size);
            }
        });

        this.socket.on('session_ended', (dimension_name, engine, message) => {
            if(engine == this.engine){
                this.connected = false;
                console.log("connection ended by neighboring tab");
            }
        });

        this.socket.on('update_hist', (dimension_name, engine, message) => {
            if(engine == this.engine){
                this.childDimension[dimension_name].histogram = JSON.parse(JSON.parse(message)['data']);
                this.childDimension[dimension_name].updateMaxMin();
                dispatchEvent(new CustomEvent('updateHistEvent', {detail: {'column': dimension_name}}));
            }
        });

        this.socket.on('update_dimension', (dimension_name, engine, message) => {
            if(engine == this.engine){
                this.childDimension[dimension_name].value = JSON.parse(JSON.parse(message)['data']);
                this.childDimension[dimension_name].updateMaxMin();
                dispatchEvent(new CustomEvent('updateDimensionEvent', {detail: {'column': dimension_name}}));
            }
        });

        this.socket.on('update_group', (dimension_name, agg, engine, message) => {
            if(engine == this.engine){
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
                // console.log(message);
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
                // console.log("schema: "+message);
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
                    console.log(error);
                    reject(error);
                    // callback(error);
                }else{
                    // console.log(message);
                    message = JSON.parse(message);
                    message['browserTime'] = (Date.now() - startTime)/1000;
                    this.connected = false;
                    resolve(message);
                }
            });
        });
    }
}

import { Group } from './group';
import { inherits } from 'util';

class Dimension{
    constructor(name, dataset, socket, engine){
        this.name = name;
        this.parent_dataset = dataset;
        this.max = 0;
        this.min = 0;
        this.socket = socket;
        this.filters = [];
        this.childGroup = {};
        this.engine = engine;
        this.value = {};
        this.histogram = {"X":{},"Y":{}};
    }

    getMax(){
        this.updateMaxMin();
        return this.max;
    }
    getMin(){
        this.updateMaxMin();
        return this.min;
    }

    //load data in gpu memory of the server, executed automatically on a successful init()
    loadDimension(){
        return new Promise((resolve,reject) => {
            let startTime = Date.now();
            this.socket.emit('dimension_load',this.name,this.parent_dataset,this.engine, (error,message) => {
                //init metadata for the current dimension
                if(error == false){
                    message = JSON.parse(message)
                    message["browserTime"] = (Date.now() - startTime)/1000;
                    this.updateMaxMin();
                    resolve(message);
                }else{
                    reject(error);
                }

            });
        });
    }

    updateMaxMin(){
        this.socket.emit('dimension_get_max_min', this.name, this.parent_dataset,this.engine,(error,message) => {
            message = JSON.parse(message);
            this.max = parseFloat(message['data'].split(",")[0].split("(")[1]);
            this.min = parseFloat(message['data'].split(",")[1].split(")")[0]);
        });
    }

    getHist(n_bins=640){
        this.socket.emit('dimension_get_hist', this.name, this.parent_dataset,n_bins,this.engine);
    }

    filterOrder(sort_order,n_rows,columns){
        this.socket.emit('dimension_filter_order',sort_order, this.name, this.parent_dataset, n_rows,columns,this.engine);
    }

    resetThenFilter(comparison=null,value=null){
        this.filters.length = 0; //clear locally stored filters
        this.filter(comparison,value, true);
    }

    filter(comparison=null,value=null, pre_reset=false){
            let already_executed = false;
            if(comparison == null && value == null){
                already_executed = true;
                this.resetFilters();
            }else if(comparison !== null && value == null){
                if(Array.isArray(comparison)){
                    already_executed = true;
                    let range = comparison;
                    this.filterRange(range,pre_reset);
                }else{
                    value = comparison;
                    comparison = "==";
                }
            }else{
                if(Array.isArray(value)){
                    if(value.length == 0){
                        already_executed = true;
                        this.resetFilters();
                    }
                }
            }
            if(already_executed == false){
                this.filters.push(comparison+""+value);
                this.socket.emit('dimension_filter',this.name,this.parent_dataset, comparison,value,this.engine, pre_reset);
            }
    }

    filterRange(range,pre_reset=false){
        const range_min = range[0];
        const range_max = range[1];
        this.filters.push('>'+range_min);
        this.filters.push('<'+range_max);
        let startTime = Date.now();
        this.socket.emit('dimension_filter_range',this.name,this.parent_dataset, range_min,range_max,this.engine, pre_reset);

    }

    //reset the dimension
    resetFilters(){
            this.filters.length = 0; //clear locally stored filters
            this.socket.emit('dimension_reset_filters', this.name, this.parent_dataset,this.engine);
    }

    top(n_rows=10, columns = []){
            this.filterOrder('top',n_rows,columns.toString());
    }

    bottom(n_rows=10, columns = []){
            this.filterOrder('bottom',n_rows,columns.toString());
    }

    all(columns=[]){
            this.filterOrder('all','null', columns.toString());
    }

    group(agg=null){
        if(agg == null){
            agg = {};
            agg[this.name] = ['mean'];
        }
        let key = this.name+JSON.stringify(agg);
        this.childGroup[key] = new Group(this.name,this.parent_dataset, this.socket,agg, this.engine);
        return this.childGroup[key];
    }
}

export { Dimension }

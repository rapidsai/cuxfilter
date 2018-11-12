class Group{
    constructor(columnName, dataset, socket, agg, engine){
        this.name = columnName;
        this.parent_dataset = dataset;
        this.socket = socket;
        this.agg = agg;
        this.size = 0;
        this.engine = engine;
        this.value = {};
    }

    //load data in gpu memory of the server, executed automatically on a successful init()
    loadGroup(){
        return new Promise((resolve,reject) => {
            let startTime = Date.now();
            this.socket.emit('groupby_load',this.name,this.parent_dataset,JSON.stringify(this.agg),this.engine, (error,message) => {
                if(error == false){
                    message = JSON.parse(message);
                    this.size = parseInt(message['size']);
                    message['browserTime'] = (Date.now()-startTime)/1000;
                    resolve(message);
                }else{
                    reject(error);
                }
            });
        });
    }

    filterOrder(sort_order,n_rows,sort_column=null){
            this.socket.emit('groupby_filter_order',sort_order, this.name, this.parent_dataset, n_rows,sort_column,JSON.stringify(this.agg),this.engine);
    }

    top(n_rows=10,sort_column= null){
        if(sort_column === null){
            const default_key = Object.keys(this.agg)[0];
            sort_column = default_key+"_"+this.agg[default_key][0];
        }
        this.filterOrder('top',n_rows,sort_column);
    }

    bottom(n_rows=10,sort_column= null){
        if(sort_column === null){
            const default_key = Object.keys(this.agg)[0];
            sort_column = default_key+"_"+this.agg[default_key][0];
        }
        this.filterOrder('bottom',n_rows,sort_column);

    }

    all(){
        this.filterOrder('all','null','null');
    }
}

export {Group}

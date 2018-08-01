var HOST = '127.0.0.1';
var PORT = 3001;
var sessId = 10;
var file = 'data-100000k';
var processing = 'numba';
var columnName = 'B';
var bins = 1024;
var net = require('net');

var pyClient = new net.Socket();

pyClient.connect(PORT,HOST);

pyClient.on("data", function(val){
    console.log(val);
});

pyClient.write("read:::data-100000k");

setTimeout(function(){
    for(var i=0; i<15;i++){
        var startTime = Date.now();
        getHist(sessId, processing,columnName,bins, function(hist){
            var response = {
                pyData: Buffer.from(hist).toString('utf8'),
                nodeServerTime: Date.now() - startTime
            }
            console.log("sending response to client");
    
        });
    }
    console.log(pyClient._events.data.toString());
    console.log(pyClient._events);

},5000);







function getHist(sessId, processing,columnName,bins, callback){
    console.log("inside the getHist function");
    pyClient.removeAllListeners(['data']);
    pyClient.on("data", function(cols){
        console.log("inside the on data callback function");
        getHistEvent =1;
        callback(cols);
    });
    
    console.log("set up the callback function");
    pyClient.write("hist:::"+sessId+":::"+processing+":::"+columnName+":::"+bins+"////");
}

//run from node-server folder not the current directory

var net = require('net');
var spawn = require('child_process').spawn;

var HOST = '127.0.0.1';
var PORT = 3001;

var pyServer = spawn('python3', ['../python_scripts/pycrossfilter.py',1]);
pyServer.stdout.on('data', function(data) {
    console.log('PyServer stdout ');
    console.log(Buffer.from(data).toString('utf8'));
    //Here is where the output goes
});
pyServer.stderr.on('data', function(data) {
    console.log('PyServer stderr ');
    console.log(Buffer.from(data).toString('utf8'));
    //Here is where the output goes
});

var client = new net.Socket();
client.connect(PORT, HOST, function() {

    console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client 
    client.write('read:::uber-dataset:::mean_travel_time///');
    client.write('dimension_load:::mean_travel_time///');
    client.write('dimension_load:::hod///');
    //client.destroy();
});

setTimeout(function(){console.log("query 1");client.write("dimension_filterOrder:::top:::mean_travel_time:::25///");},2000);

setTimeout(function(){console.log("query 2");client.write("dimension_filter_range:::mean_travel_time:::100:::200///");},3000);

setTimeout(function(){console.log("query 3");client.write("dimension_filter:::hod:::<:::10///");},3500);

setTimeout(function(){console.log("query 4");client.write("dimension_reset:::mean_travel_time///");},4000);

setTimeout(function(){console.log("exiting...");client.write("exit");client.destroy();console.log("test successful if you see no errors upto this point")},8000);

// Add a 'data' event handler for the client socket
// data is what the server sent to this socket
client.on('data', function(data) {
    console.log('pyClient DATA: ' + data);
});

// Add a 'close' event handler for the client socket
client.on('close', function() {
    console.log('Connection closed');
});
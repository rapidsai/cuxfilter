var net = require('net');

var HOST = '127.0.0.1';
var PORT = 3001;

var client = new net.Socket();
client.connect(PORT, HOST, function() {

    console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client 
    client.write('read:::uber-dataset');
    
    //client.destroy();
});

setTimeout(function(){client.write("hello");client.destroy();},4000);

// Add a 'data' event handler for the client socket
// data is what the server sent to this socket
client.on('data', function(data) {
    
    console.log('DATA: ' + data);
    //client.write('exit');
    // Close the client socket completely
    
});

// Add a 'close' event handler for the client socket
client.on('close', function() {
    console.log('Connection closed');
});
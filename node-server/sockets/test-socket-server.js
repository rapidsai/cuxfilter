let chunks = [];

var spawn = require('child_process').spawn;  
var py = spawn('python', ['../python-scripts/socket-testing/temp_server.py']);

// setTimeout(function(){
//     var pyclient = spawn('node', ['sockets/test-socket-client.js']);

//     pyclient.stdout.on('data', function(val){
//         console.log(val);
//     });
//     pyclient.on('exit', function(){
//         console.log("exiting client");
//     });
// }, 4000);

py.stdout.on('data', function(val){
    console.log(JSON.stringify(val));
});

py.on('exit', function(){
    console.log("exiting");
});



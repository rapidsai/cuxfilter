var http = require('http'),
    fs = require('fs'),
    cors = require('cors'),
    nvidia_smi_usage = require('./utilities/nvidia_smi'),
    connect = require('connect');
// NEVER use a Sync function except at start-up!
let index = fs.readFileSync(__dirname + '/index.html');

let whitelist = ['http://localhost:3000','http://localhost:9000'];
let corsOptions = {
  origin: (origin, callback)=>{
      if (whitelist.indexOf(origin) !== -1) {
          callback(null, true)
      } else {
          callback(new Error('Not allowed by CORS'))
      }
  },credentials: true
}
var app = connect()
    .use(cors(corsOptions))

    .use(function(req, res){
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.end(index);
 });

// Send index.html to all requests
var server = http.createServer(app);

// Socket.io server listens to our app
var io = require('socket.io').listen(server);

// Send current time to all connected clients
function sendGPUMemUsage() {
  nvidia_smi_usage().then(res => {
    io.emit('GPUMemUsage', res);
  });
}


// Emit welcome message on connection
io.on('connection', function(socket) {
  console.log("connected")
    // Send current memory usage every 1 secs
    setInterval(sendGPUMemUsage, 1000);

});

server.listen(3004);

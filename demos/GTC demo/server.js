// node express server
// initialize the server
import path from 'path';
import { Server } from 'http';
import Express from 'express';

const app = new Express();
const server = new Server(app);


// Express
// define the folder that will be used for static assets
app.use(Express.static(path.join(__dirname, '/public')));

// # routing handled by react
app.get('/', (req, res) => {
      
      // return react
      return res.sendFile(path.join(__dirname+'/public/index.html'));
});

// error
app.use(function (err, req, res, next) {
  console.error(err.stack)
  res.status(500).send('500: Something broke.')
})

// 404 catch 
app.use(function (req, res, next) {
  res.status(404).send("404: Sorry can't find that.")
})

// start the server
const port = process.env.PORT || 3000;
const env = process.env.NODE_ENV || 'production';
server.listen(port, err => {
  if (err) {
    return console.error(err);
  }
  console.info(`Server running on http://localhost:${port} [${env}]`);
});


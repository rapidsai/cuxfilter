var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var cors = require('cors');
//using the session variable to track unique user sessions
var session = require('express-session');
var sharedSession = require("express-socket.io-session");
//for file upload handling
var connect = require('connect');


var sessionMiddleware = session({
  secret: 'mouse dog',
  resave: true,
  saveUninitialized: true});


var app = express();
app.io = require('socket.io')({
  path: '/pygdfCrossfilter'
});

// enable cors
let whitelist = ['http://localhost:3000','http://localhost:3002','http://localhost:9000'];
let corsOptions = {
    origin: (origin, callback)=>{
        if (whitelist.indexOf(origin) !== -1) {
            callback(null, true)
        } else {
            callback(new Error('Not allowed by CORS'))
        }
    },credentials: true
}
app.use(cors());
app.use(cors(corsOptions));
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(function (req, res, next) {
    res.header('Cache-Control', 'private, no-cache, no-store');
    next()
});
app.use(sessionMiddleware);

var pygdfCrossfilter = require('./routes/pygdfCrossfilter')(app.io);

app.use('/pygdfCrossfilter',pygdfCrossfilter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});



module.exports = app;

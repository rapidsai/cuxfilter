var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var cors = require('cors');
//using the session variable to track unique user sessions
var session = require('express-session');
//for file upload handling
var multer = require('multer');

var sessionMiddleware = session({
  secret: 'mouse dog',
  resave: true,
  saveUninitialized: true
});


var sharedSession = require('express-socket.io-session');


const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/')
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname.split(".")[0])
  }
})


var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var upload = require('./routes/upload');
var calc = require('./routes/calc');
var socket_calc = require('./routes/socket-calc');

var app = express();


app.io = require('socket.io')({
  path: '/pycrossfilter'
});
var pycrossfilter = require('./routes/pycrossfilter')(app.io);


app.set('file_path','Hello World!');
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

//enable cors
app.use(cors({origin: '*'}));
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(multer({dest: "./uploads/",storage: storage}).any());

app.use(sessionMiddleware);
app.io.use(sharedSession(sessionMiddleware,{
  autoSave:true
}));

app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/upload',upload);
app.use('/calc',calc);
app.use('/socket-calc',socket_calc);
app.use('/pycrossfilter',pycrossfilter);

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

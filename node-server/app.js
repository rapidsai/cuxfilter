var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var cors = require('cors');

//for file upload handling
var multer = require('multer');

//using the session variable to track unique user sessions
var session = require('express-session');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var upload = require('./routes/upload');
var calc = require('./routes/calc');
var app = express();



app.set('file_path','Hello World!');
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

//enable cors
app.use(cors({origin: '*'}));

app.use(session({
  genid: function(req) {
    return genuuid() // use UUIDs for session IDs
  },
  secret: 'mouse dog',
  resave: true,
  saveUninitialized: true
}));


app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use(multer({dest: "./uploads/"}).any());

app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/upload',upload);
app.use('/calc',calc);
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


function genuuid(){
  return new Date();
}


module.exports = app;

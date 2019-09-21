# app/__init__.py

# from flask import Flask
from sanic import Sanic

# Initialize the app
# app = Flask(__name__, instance_relative_config=True)
app = Sanic(__name__)

# Load the views
from app import views

# Load the config file
app.config.from_object('config')
app.debug = True

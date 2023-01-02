from flask import Flask,render_template,redirect,request,flash,url_for,session
from flask_bcrypt import Bcrypt



app=Flask(__name__)

app.config['SECRET_KEY']='hello'

bcrypt=Bcrypt(app)

from Market import routes
from Market.models import get_user_details
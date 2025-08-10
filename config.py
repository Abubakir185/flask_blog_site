from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment

db = SQLAlchemy()

app = Flask(__name__)
moment = Moment(app)
app.config['SECRET_KEY'] = '8A76b56f8He34M4a88debQ582ea187b6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from models import User, Post, Comment, Category

login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()
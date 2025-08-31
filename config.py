import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_moment import Moment
from dotenv import load_dotenv

# .env fayldan o‘qish
load_dotenv()

# Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# PostgreSQL ulanish (DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/dbname")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions init
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
moment.init_app(app)

# Login uchun redirect qilingan sahifa
login_manager.login_view = 'login'

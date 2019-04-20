from flask import Flask
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = str(secrets.token_hex(16))
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_menager = LoginManager(app)
login_menager.login_view = 'login'
login_menager.login_message_category = 'info'

from app import routes
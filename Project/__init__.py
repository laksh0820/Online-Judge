from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv("./.env")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {'problems':'sqlite:///problem_set.db','submissions':'sqlite:///submissions.db'}   
app.config['SECRET_KEY'] = 'projectzetaxksdkar37ro8hf83fh3892hmfijw38fh'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=20)
app.config['SECURITY_PASSWORD_SALT']='email-confirmation-for-a-new-user//projectzetaX//23jnrxnl4r'
app.config['MAIL_DEFAULT_SENDER'] = os.environ['USERNAME']
app.config['MAIL_PORT'] = 465
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = os.getenv('USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('APP_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'

db = SQLAlchemy(app)
mail = Mail(app)

from Project import routes
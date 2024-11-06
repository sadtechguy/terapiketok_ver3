import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

ENV = os.getenv("ENV")
if ENV == "DEV":
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@localhost:5432/{DATABASE_NAME}"
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = 1800
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ""

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from terapiketok.routes.home import home_bp
from terapiketok.routes.boardpanel import boardpanel_bp

app.register_blueprint(home_bp)
app.register_blueprint(boardpanel_bp)


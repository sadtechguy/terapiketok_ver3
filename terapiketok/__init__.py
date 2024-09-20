import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ""

db = SQLAlchemy(app)

from terapiketok.routes.home import home_bp

app.register_blueprint(home_bp)


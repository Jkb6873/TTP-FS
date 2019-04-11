import os

from .config import APP_SECRET, SQLALCHEMY_DATABASE_URI
from .utils import CustomEncoder
from .routes.controller import api
from .database import db
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = APP_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.json_encoder = CustomEncoder
    app.register_blueprint(api)
    db.init_app(app)
    return app

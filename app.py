from flask import Flask, jsonify
# from src.routers.home import home

from config import Config
from src.database.db import init_db


def app_create(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        init_db()

    app.config.from_object(Config)

    # app.register_blueprint(home)

    return app
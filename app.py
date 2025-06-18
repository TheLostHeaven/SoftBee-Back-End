from flask import Flask, jsonify
# from src.routers.home import home

from config import Config
from src.database.db import init_app, get_db, close_db, init_database


def app_create(testing=False):
    app = Flask(__name__)
    app.config['DATABASE'] = 'database.db'
    app.config.from_object(Config)

    with app.app_context():
        init_app(app)
        db = get_db()
        init_database(db)
        close_db(db) 

    app.config.from_object(Config)

    # app.register_blueprint(home)


    return app
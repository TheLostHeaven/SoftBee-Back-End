#App donde se inicializa y configura las rutas de la app 
from flask import Flask, jsonify
# from src.routers.home import home
# from src.routers.auth import auth
# from src.routers.user import user
# from src.routers.tours import tours
# from src.routers.reserves import reserve
from config import Config
from src.database.db import init_db


def app_create(testing=False): #Se puede activar y desactiva los testing 
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        init_db()

    app.config.from_object(Config)

    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # db.init_app(app)

    # app.register_blueprint(home)
    # app.register_blueprint(auth)
    # app.register_blueprint(user)
    # app.register_blueprint(tours)
    # app.register_blueprint(reserve)

    return app
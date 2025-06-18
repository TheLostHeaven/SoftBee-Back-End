from flask import Flask, jsonify
# from src.routers.home import home
from src.routes.question import question_bp
from config import Config
from src.database.db import init_app, get_db, close_db, init_database
from src.routes.inventory import inventory_bp


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
    app.register_blueprint(question_bp, url_prefix='/api')
      # Registrar blueprints
    app.register_blueprint(inventory_bp)


    return app
from flask import Flask
from flask_cors import CORS
import os
#from src.routes.users import user_bp

from config import Config

def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    CORS(app)
    
    
    from src.database.db import init_app
    init_app(app)

    # Registrar blueprints
    from src.routes.apiary import create_apiary_routes
    from src.routes.beehive import create_hive_routes
    from src.routes.inventory import create_inventory_routes
    from src.routes.question import create_question_routes
    from src.routes.users import create_user_routes
    from src.routes.auth import create_auth_routes

    app.register_blueprint(create_apiary_routes(), url_prefix='/api')
    app.register_blueprint(create_hive_routes(), url_prefix='/api')
    app.register_blueprint(create_inventory_routes(), url_prefix='/api')
    app.register_blueprint(create_question_routes(), url_prefix='/api')
    app.register_blueprint(create_user_routes(), url_prefix='/api')
    app.register_blueprint(create_auth_routes(), url_prefix='/api')

    return app

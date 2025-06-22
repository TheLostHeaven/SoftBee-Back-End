from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from src.utils.email_service import EmailService
import os
#from src.routes.users import user_bp

from config import Config

def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    CORS(app)
    mail = Mail(app)
    email_service = EmailService(mail)
    
    
    from src.database.db import init_app
    init_app(app)

    from src.routes.apiary import create_apiary_routes
    from src.routes.beehive import create_hive_routes
    from src.routes.inventory import create_inventory_routes
    from src.routes.question import create_question_routes
    from src.routes.users import create_user_routes
    from src.routes.auth import create_auth_routes


    with app.app_context():
        app.register_blueprint(create_apiary_routes(), url_prefix='/api')
        app.register_blueprint(create_hive_routes(), url_prefix='/api')
        app.register_blueprint(create_inventory_routes(), url_prefix='/api')
        app.register_blueprint(create_question_routes(), url_prefix='/api')
        app.register_blueprint(create_user_routes(), url_prefix='/api')
        app.register_blueprint(create_auth_routes(email_service), url_prefix='/api')


    # Registrar blueprints




    return app

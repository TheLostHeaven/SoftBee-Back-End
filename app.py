from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from src.utils.email_service import EmailService
from src.utils.file_handler import FileHandler
from src.database.db import get_db
from config import Config
from datetime import datetime
from flask.json.provider import DefaultJSONProvider 

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        return super().default(obj)

def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)

    app.json_provider_class = CustomJSONProvider
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    file_handler = FileHandler()
    file_handler.init_app(app)
    app.file_handler = file_handler

    from src.database.db import init_app
    init_app(app)

    from src.routes.apiary import create_apiary_routes
    from src.routes.beehive import create_hive_routes
    from src.routes.inventory import create_inventory_routes
    from src.routes.question import create_question_routes
    from src.routes.users import create_user_routes
    from src.routes.auth import create_auth_routes
    from src.routes.monitoreo import create_monitoreo_routes
    from src.routes.reports import create_reports_routes

    mail = Mail(app)
    email_service = EmailService(mail)

    with app.app_context():
        auth_bp = create_auth_routes(get_db_func=get_db, email_service=email_service)
        app.register_blueprint(auth_bp, url_prefix='/api')

    app.register_blueprint(create_apiary_routes(), url_prefix='/api')
    app.register_blueprint(create_hive_routes(), url_prefix='/api')
    app.register_blueprint(create_inventory_routes(), url_prefix='/api')
    app.register_blueprint(create_question_routes(), url_prefix='/api')
    app.register_blueprint(create_user_routes(), url_prefix='/api')
    app.register_blueprint(create_monitoreo_routes(), url_prefix='/api')
    app.register_blueprint(create_reports_routes(), url_prefix='/api')

    return app

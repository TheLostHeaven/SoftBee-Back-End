from dotenv import load_dotenv
import os

# Cargar el archivo .env principal primero
load_dotenv()

# Obtener el entorno después de cargar .env
environment = os.getenv('FLASK_ENV', 'local')

# Intentar cargar archivo específico del entorno si existe
env_file = f'.env.{environment}'
if os.path.exists(env_file):
    load_dotenv(env_file, override=True)

DATABASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuración base para todos los entornos"""
    
    # Configuración general
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración de correo
    MAIL_SERVER = os.getenv("SMTP_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("SMTP_PORT", 587))
    MAIL_USERNAME = os.getenv("SMTP_USER")
    MAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = os.getenv("SMTP_USER")

    # Configuración de JWT
    JWT_SECRET_KEY = os.getenv("JWT_KEY", "secret-key-default")
    JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("EXPIRES_TOKEN_SESSION", 1440))  # 24 horas
    JWT_RESET_TOKEN_EXPIRES = int(os.getenv("EXPIRES_TOKEN_EMAIL", 30))  # 30 minutos
    
    # URLs base
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

class LocalConfig(Config):
    """Configuración para entorno local"""
    DEBUG = True
    TESTING = False
    
    # Base de datos PostgreSQL local para desarrollo
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/softbee_local")
    
    # URLs para desarrollo local
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo (servidor de desarrollo)"""
    DEBUG = True
    TESTING = False
    
    # Base de datos PostgreSQL de desarrollo
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/softbee_dev")

class ProductionConfig(Config):
    """Configuración para entorno de producción"""
    DEBUG = False
    TESTING = False
    
    # Base de datos PostgreSQL de producción (debe venir de variable de entorno)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Validar que existan las variables críticas en producción
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL es requerida en producción")
    
    if not os.getenv("JWT_KEY"):
        raise ValueError("JWT_KEY es requerida en producción")
    
    if not os.getenv("SECRET_KEY"):
        raise ValueError("SECRET_KEY es requerida en producción")

class TestingConfig(Config):
    """Configuración para pruebas"""
    DEBUG = True
    TESTING = True
    
    # Base de datos PostgreSQL para tests
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/softbee_test")
    
    # Desactivar protecciones para facilitar testing
    WTF_CSRF_ENABLED = False

# Diccionario de configuraciones disponibles
config = {
    'local': LocalConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': LocalConfig
}

def get_config():
    """Obtiene la configuración basada en la variable de entorno FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'local')
    return config.get(env, config['default'])
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    
    MAIL_SERVER = os.getenv("SMTP_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("SMTP_PORT", 587))
    MAIL_USERNAME = os.getenv("SMTP_USER")
    MAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = os.getenv("SMTP_USER")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-default")
    JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("EXPIRES_TOKEN_SESSION", 1440))  # 24 horas
    JWT_RESET_TOKEN_EXPIRES = int(os.getenv("EXPIRES_TOKEN_EMAIL", 30))  # 30 minutos
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///instance/database.db")
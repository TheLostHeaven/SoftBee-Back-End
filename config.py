from dotenv import load_dotenv
import os 

load_dotenv()

DATABASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config():
    DATABASE = os.path.join(DATABASE_DIR, 'database.db')
    debug = True


smtpHost = os.environ["SMTP_HOST"]
smtpPort = int(os.environ["SMTP_PORT"])
smtpUser = os.environ["SMTP_USER"]
smtpPassword = os.environ["SMTP_PASSWORD"]
front_end_url = os.environ["FRONTEND_URL"]
secretKey = os.environ["SECRET_KEY"]
algorithm = os.environ["ALGORITHM"]
expiresTokenEmail = int(os.environ["EXPIRES_TOKEN_EMAIL"])
expiresTokenSession = int(os.environ["EXPIRES_TOKEN_SESSION"]) 
jwtKey = os.environ["JTW_KEY"]

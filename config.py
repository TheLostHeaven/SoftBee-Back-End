from dotenv import load_dotenv
import os 

load_dotenv()

DATABASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config():
    DATABASE = os.path.join(DATABASE_DIR, 'database.db')
    debug = True


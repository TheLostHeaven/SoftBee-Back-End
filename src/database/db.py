import sqlite3
from flask import g
from config import Config
from src.models.users import init as init_users
from src.models.apiary import init as init_apiary
from src.models.beehive import init as init_beehive
from src.models.questions import init as init_question
from src.models.inspection import init as init_inspection
from src.models.apiary_access import init as init_apiary_access
from src.models.beehive import init as init_beehive

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(Config.DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

def init_db():
    db = get_db()
    init_users(db)
    init_apiary(db)
    init_beehive(db)
    init_question(db)
    init_inspection(db)
    init_apiary_access(db)
    db.commit()


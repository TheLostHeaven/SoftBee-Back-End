from app import app_create

from src.database.db import get_db, close_db, init_database


app = app_create()

if __name__ == '__main__':
    app = app_create()
    app.run(debug=True)
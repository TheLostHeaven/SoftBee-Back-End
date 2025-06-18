from app import app_create
import os

from src.database.db import get_db, close_db, init_database


app = app_create()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = app_create()
    app.run(debug=True)
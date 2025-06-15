from app import app_create

from src.database.db import get_db, create_all_tables
db = get_db()
create_all_tables(db)
db.commit()

app = app_create()

if __name__ == '__main__':
    app = app_create()
    app.run(debug=True)
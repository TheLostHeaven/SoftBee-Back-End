import sqlite3
import os

DB_PATH = os.path.join('instance', 'app.db')

def reset_questions():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS questions")
        print("Tabla questions eliminada.")
        conn.commit()

        from src.models.questions import QuestionModel
        QuestionModel.init_db(conn)
        print("Tabla questions creada.")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_questions()

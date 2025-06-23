from base_model import BaseModel
from datetime import datetime, timedelta

class NotificationModel(BaseModel):

    @staticmethod
    def init_db(db):
        """Inicializa la tabla de notificaciones"""
        cursor = db.cursor()
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                is_archived BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE,
                priority INTEGER DEFAULT 0,
                expires_at DATETIME,
                url:actions TEXT,
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                read_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

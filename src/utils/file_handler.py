import os
import time
from werkzeug.utils import secure_filename

class FileHandler:
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'profile_pictures')
        app.config.setdefault('PROFILE_PICTURES_FOLDER', self.UPLOAD_FOLDER)
        app.config.setdefault('MAX_CONTENT_LENGTH', 2 * 1024 * 1024)  # 2MB
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        # Crear directorio si no existe
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
    
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def save_profile_picture(self, file, user_id):
        if not file or file.filename == '':
            return None
        
        if not self.allowed_file(file.filename):
            return None
        
        # Generar nombre seguro y único
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_{user_id}_{int(time.time())}.{ext}"
        filepath = os.path.join(self.UPLOAD_FOLDER, filename)
        
        file.save(filepath)
        return filename
    
    def get_profile_picture_url(self, filename):
        if not filename:
            filename = 'profile_picture.png'
        return f"/static/profile_pictures/{filename}"
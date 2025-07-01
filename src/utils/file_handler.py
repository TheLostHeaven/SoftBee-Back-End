import os
import time
from werkzeug.utils import secure_filename

class FileHandler:
    def _init_(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'profile_pictures')
        
        app.config.setdefault('PROFILE_PICTURES_FOLDER', self.UPLOAD_FOLDER)
        app.config.setdefault('MAX_CONTENT_LENGTH', 2 * 1024 * 1024)  # 2MB
        app.config.setdefault('BASE_URL', "")

        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
    
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def save_profile_picture(self, file, user_id):
        if not file or file.filename == '':
            return None
        
        if not self.allowed_file(file.filename):
            return None
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_{user_id}_{int(time.time())}.{ext}"
        filepath = os.path.join(self.UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filename

    def get_profile_picture_url(self, filename):
        base_url = self.app.config.get("BASE_URL", "http://localhost:5000")

        if not filename or filename in ['profile_picture.png', 'default_profile.jpg']:
            return f"{base_url}/static/profile_pictures/userSoftbee.png"
        
        return f"{base_url}/static/profile_pictures/{filename}"
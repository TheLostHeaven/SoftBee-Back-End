"""
Modelos SQLAlchemy para migraciones
Este archivo define todos los modelos usando SQLAlchemy ORM para que Flask-Migrate
pueda detectar automáticamente los cambios y generar migraciones.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class UserTypeEnum(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255))
    user_type = db.Column(db.Enum(UserTypeEnum), default=UserTypeEnum.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    apiaries = db.relationship('Apiary', backref='owner', lazy=True, cascade='all, delete-orphan')
    apiary_accesses = db.relationship('ApiaryAccess', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación
    user = db.relationship('User', backref='reset_tokens')
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token}>'

class Apiary(db.Model):
    __tablename__ = 'apiaries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    hives = db.relationship('Hive', backref='apiary', lazy=True, cascade='all, delete-orphan')
    apiary_accesses = db.relationship('ApiaryAccess', backref='apiary', lazy=True, cascade='all, delete-orphan')
    inventory_items = db.relationship('Inventory', backref='apiary', lazy=True, cascade='all, delete-orphan')
    monitoreos = db.relationship('Monitoreo', backref='apiary', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Apiary {self.name}>'

class AccessLevelEnum(enum.Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class ApiaryAccess(db.Model):
    __tablename__ = 'apiary_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    apiary_id = db.Column(db.Integer, db.ForeignKey('apiaries.id'), nullable=False)
    access_level = db.Column(db.Enum(AccessLevelEnum), default=AccessLevelEnum.READ, nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relación con el usuario que otorgó el acceso
    granter = db.relationship('User', foreign_keys=[granted_by])
    
    # Índice único para evitar accesos duplicados
    __table_args__ = (db.UniqueConstraint('user_id', 'apiary_id', name='unique_user_apiary_access'),)
    
    def __repr__(self):
        return f'<ApiaryAccess user:{self.user_id} apiary:{self.apiary_id} level:{self.access_level.value}>'

class HiveStatusEnum(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    LOST = "lost"

class Hive(db.Model):
    __tablename__ = 'hives'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    apiary_id = db.Column(db.Integer, db.ForeignKey('apiaries.id'), nullable=False)
    location_in_apiary = db.Column(db.String(100))  # Por ejemplo: "Fila 1, Columna 3"
    hive_type = db.Column(db.String(50))  # Langstroth, Top Bar, etc.
    installation_date = db.Column(db.Date)
    status = db.Column(db.Enum(HiveStatusEnum), default=HiveStatusEnum.ACTIVE, nullable=False)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    inspections = db.relationship('Inspection', backref='hive', lazy=True, cascade='all, delete-orphan')
    monitoreos = db.relationship('Monitoreo', backref='hive', lazy=True)
    
    def __repr__(self):
        return f'<Hive {self.name}>'

class Inspection(db.Model):
    __tablename__ = 'inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    hive_id = db.Column(db.Integer, db.ForeignKey('hives.id'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    weather_conditions = db.Column(db.String(100))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    
    # Observaciones de la colmena
    queen_present = db.Column(db.Boolean)
    queen_laying = db.Column(db.Boolean)
    brood_pattern = db.Column(db.String(50))  # excellent, good, fair, poor
    population_level = db.Column(db.String(50))  # high, medium, low
    
    # Estado de la colmena
    disease_signs = db.Column(db.Boolean, default=False)
    disease_description = db.Column(db.Text)
    pest_presence = db.Column(db.Boolean, default=False)
    pest_description = db.Column(db.Text)
    
    # Producción
    honey_production = db.Column(db.Float)  # kg
    frames_with_honey = db.Column(db.Integer)
    frames_with_brood = db.Column(db.Integer)
    
    # Acciones realizadas
    actions_taken = db.Column(db.Text)
    medication_applied = db.Column(db.String(255))
    
    # Observaciones generales
    general_notes = db.Column(db.Text)
    next_inspection_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación
    inspector = db.relationship('User', backref='inspections')
    
    def __repr__(self):
        return f'<Inspection {self.id} - Hive {self.hive_id}>'

class InventoryTypeEnum(enum.Enum):
    EQUIPMENT = "equipment"
    MEDICATION = "medication"
    FOOD = "food"
    TOOL = "tool"
    CONSUMABLE = "consumable"

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    apiary_id = db.Column(db.Integer, db.ForeignKey('apiaries.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    item_type = db.Column(db.Enum(InventoryTypeEnum), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit = db.Column(db.String(20))  # kg, units, liters, etc.
    minimum_stock = db.Column(db.Integer, default=0)
    purchase_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    supplier = db.Column(db.String(100))
    cost = db.Column(db.Float)
    location = db.Column(db.String(100))  # Dónde está almacenado
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inventory {self.name} - {self.quantity} {self.unit}>'

class QuestionTypeEnum(enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    TEXT = "text"
    SCALE = "scale"

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionTypeEnum), nullable=False)
    category = db.Column(db.String(50))  # inspection, health, production, etc.
    options = db.Column(db.JSON)  # Para preguntas de opción múltiple
    is_required = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.text[:50]}...>'

class Monitoreo(db.Model):
    __tablename__ = 'monitoreo'
    
    id = db.Column(db.Integer, primary_key=True)
    apiary_id = db.Column(db.Integer, db.ForeignKey('apiaries.id'), nullable=False)
    hive_id = db.Column(db.Integer, db.ForeignKey('hives.id'), nullable=True)  # Puede ser NULL si es monitoreo general del apiario
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Datos ambientales
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    weight = db.Column(db.Float)  # Peso de la colmena
    
    # Datos de actividad
    bee_activity_level = db.Column(db.String(20))  # high, medium, low
    entrance_activity = db.Column(db.Integer)  # Abejas contadas en la entrada
    
    # Datos del sensor o manual
    is_automated = db.Column(db.Boolean, default=False)  # Si viene de sensores automáticos
    sensor_data = db.Column(db.JSON)  # Datos adicionales del sensor
    
    # Observaciones manuales
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Monitoreo {self.id} - Apiary {self.apiary_id}>'
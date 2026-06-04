# backend/models.py
import uuid
from datetime import datetime
from . import db # Импортируем db из backend/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Reagent(db.Model):
    __tablename__ = 'reagents'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    manufacturer = db.Column(db.Text)
    status = db.Column(db.Text, default='active') # 'active', 'archived'
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношение к документам: 'lazy=True' означает, что документы будут загружены только при обращении к ним.
    # 'cascade="all, delete-orphan"' гарантирует удаление документов при удалении реагента.
    documents = db.relationship('Document', backref='reagent', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Reagent {self.name}>'

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reagent_id = db.Column(db.String(36), db.ForeignKey('reagents.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    document_type = db.Column(db.Text, nullable=False) # 'ГОСТ', 'ТУ', 'MSDS', 'Сертификат' и т.д.
    file_path = db.Column(db.Text, nullable=False) # Путь к файлу на сервере
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Document {self.name}>'
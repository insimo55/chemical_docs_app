# backend/__init__.py (ОБНОВЛЕННЫЙ И РАСШИРЕННЫЙ КОД)

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .config import Config

# Инициализация расширений на уровне пакета
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app():
    app = Flask(__name__)
    # Импортируем Config из config.py в текущем пакете
    app.config.from_object(Config)

    # Инициализация расширений с приложением
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Создаем папку для загруженных файлов, если её нет
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Импорт моделей (это важно для обнаружения моделей Alembic'ом)
    from . import models

    # Импорт и регистрация Blueprints
    # (Это нужно делать ПОСЛЕ импорта моделей, чтобы избежать круговых зависимостей
    # если Blueprints зависят от моделей)
    from .routes.auth import auth_bp
    from .routes.reagents import reagents_bp
    from .routes.documents import documents_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(reagents_bp, url_prefix='/api/reagents')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')

    # Примеры обработчиков для JWT
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return {'message': 'Missing Authorization Header'}, 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return {'message': 'Signature verification failed'}, 403

    @app.route('/')
    def hello():
        return "Welcome to Chemical Docs API!"

    return app

# Если запускаем пакет напрямую (например, 'python -m backend' для теста)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
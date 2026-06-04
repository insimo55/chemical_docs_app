# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Загружаем переменные окружения из .env файла

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'a_very_secret_default_key_replace_me'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///default.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') # Используем тот же ключ для JWT
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.environ.get('UPLOAD_FOLDER', 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Максимальный размер файла 16MB

    # Разрешенные расширения файлов
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpeg', 'jpg', 'png', 'tiff'}

    # Проверка, что секретный ключ установлен, иначе предупреждение
    if not JWT_SECRET_KEY or JWT_SECRET_KEY == 'YOUR_JWT_SECRET_KEY_VERY_STRONG_AND_RANDOM':
        print("WARNING: JWT_SECRET_KEY is not set or is default. Please set a strong random key in your .env file!")
# backend/utils/file_manager.py
import os
import uuid
import re
from flask import current_app

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def sanitize_filename_cyrillic(filename):
    """
    Очищает имя файла от запрещенных символов файловой системы Windows/Linux,
    но полностью сохраняет русские буквы (кириллицу) и пробелы.
    """
    # Удаляем символы: \ / * ? : " < > |
    cleaned = re.sub(r'[\\/*?:"<>|]', '', filename)
    # Ограничиваем длину имени файла до 150 символов во избежание проблем с ФС
    cleaned = cleaned[:150].strip()
    if not cleaned:
        cleaned = "document"
    return cleaned

def save_file(file, reagent_id):
    if not file:
        return None, "No file provided"

    if not allowed_file(file.filename):
        return None, "File type not allowed"

    # Извлекаем расширение напрямую из оригинального имени файла
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    
    # Генерируем уникальный UUID для безопасного хранения на сервере
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

    reagent_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(reagent_id))
    if not os.path.exists(reagent_folder):
        os.makedirs(reagent_folder)

    file_path = os.path.join(reagent_folder, unique_filename)
    file.save(file_path)
    
    # Возвращаем относительный путь
    return os.path.relpath(file_path, current_app.root_path), None

def delete_file(file_path):
    full_path_to_delete = os.path.join(current_app.root_path, file_path)
    if full_path_to_delete and os.path.exists(full_path_to_delete):
        os.remove(full_path_to_delete)
        reagent_folder = os.path.dirname(full_path_to_delete)
        if not os.listdir(reagent_folder):
            os.rmdir(reagent_folder)
        return True
    return False

def get_file_full_path_for_download(db_file_path):
    if not db_file_path:
        return None, None
    full_abs_path = os.path.join(current_app.root_path, db_file_path)
    directory = os.path.dirname(full_abs_path)
    filename = os.path.basename(full_abs_path)
    return directory, filename
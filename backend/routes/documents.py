# backend/routes/documents.py
import os
import zipfile
import io
from flask import Blueprint, request, jsonify, send_from_directory, current_app, send_file
from flask_jwt_extended import jwt_required
from datetime import datetime

# Импортируем из нашего пакета backend
from .. import db
from ..models import Reagent, Document
from ..utils import file_manager 
# Импортируем наш новый санитайзер
from ..utils.file_manager import sanitize_filename_cyrillic

documents_bp = Blueprint('documents', __name__)

# Маршрут для загрузки нового документа
@documents_bp.route('/upload/<string:reagent_id>', methods=['POST'])
@jwt_required()
def upload_document(reagent_id):
    reagent = Reagent.query.get(reagent_id)
    if not reagent:
        return jsonify({'message': 'Reagent not found'}), 404

    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if len(file.read()) > current_app.config['MAX_CONTENT_LENGTH']:
        file.seek(0)
        return jsonify({'message': f"File size exceeds limit"}), 413
    file.seek(0)

    file_path, error = file_manager.save_file(file, reagent_id)
    if error:
        return jsonify({'message': error}), 400

    name = request.form.get('name') or file.filename
    document_type = request.form.get('document_type', 'Другое')
    valid_from_str = request.form.get('valid_from')
    valid_until_str = request.form.get('valid_until')

    valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d').date() if valid_from_str else None
    valid_until = datetime.strptime(valid_until_str, '%Y-%m-%d').date() if valid_until_str else None

    # Принудительно приводим is_active к булевому типу (из форм-даты приходит строкой "true"/"false")
    is_active_form = request.form.get('is_active', 'true')
    is_active = is_active_form.lower() in ['true', '1', 'yes']

    new_document = Document(
        reagent_id=reagent.id,
        name=name,
        document_type=document_type,
        file_path=file_path,
        valid_from=valid_from,
        valid_until=valid_until,
        is_active=is_active
    )
    db.session.add(new_document)
    db.session.commit()

    return jsonify({
        'message': 'Document uploaded successfully',
        'document': {
            'id': new_document.id,
            'name': new_document.name,
            'document_type': new_document.document_type,
            'valid_from': new_document.valid_from.isoformat() if new_document.valid_from else None,
            'valid_until': new_document.valid_until.isoformat() if new_document.valid_until else None,
        }
    }), 201

# Маршрут для скачивания конкретного документа (ОДИНОЧНОЕ СКАЧИВАНИЕ)
@documents_bp.route('/download/<string:document_id>', methods=['GET'])
@jwt_required()
def download_document(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    target_directory, target_filename = file_manager.get_file_full_path_for_download(document.file_path)

    if not target_directory or not os.path.exists(os.path.join(target_directory, target_filename)):
        return jsonify({'message': 'File not found on server'}), 404

    # Получаем расширение оригинального файла на диске
    original_ext = os.path.splitext(target_filename)[1]
    
    # Формируем русское название для скачивания на основе document.name из БД
    download_name_from_db = sanitize_filename_cyrillic(document.name) + original_ext

    return send_from_directory(
        directory=target_directory,
        path=target_filename,
        as_attachment=True,
        download_name=download_name_from_db # Отдаем браузеру оригинальное русское имя
    )

# Маршрут для получения метаданных документа
@documents_bp.route('/<string:document_id>', methods=['GET'])
@jwt_required()
def get_document_metadata(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    doc_validity_status = "Unknown"
    if document.valid_until:
        today = datetime.now().date()
        if document.valid_until < today:
            doc_validity_status = "Expired"
        elif (document.valid_until - today).days <= 30:
            doc_validity_status = "Expires soon"
        else:
            doc_validity_status = "Active"
    elif document.valid_until is None:
         doc_validity_status = "Active (perpetual)"

    return jsonify({
        'id': document.id,
        'reagent_id': document.reagent_id,
        'name': document.name,
        'document_type': document.document_type,
        'valid_from': document.valid_from.isoformat() if document.valid_from else None,
        'valid_until': document.valid_until.isoformat() if document.valid_until else None,
        'is_active': document.is_active,
        'validity_status': doc_validity_status,
        'created_at': document.created_at.isoformat(),
        'updated_at': document.updated_at.isoformat()
    }), 200

# Маршрут для обновления метаданных документа
@documents_bp.route('/<string:document_id>', methods=['PUT'])
@jwt_required()
def update_document_metadata(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    data = request.get_json()
    document.name = data.get('name', document.name)
    document.document_type = data.get('document_type', document.document_type)
    document.is_active = data.get('is_active', document.is_active)

    valid_from_str = data.get('valid_from')
    valid_until_str = data.get('valid_until')

    if valid_from_str is not None:
        document.valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d').date() if valid_from_str else None
    if valid_until_str is not None:
        document.valid_until = datetime.strptime(valid_until_str, '%Y-%m-%d').date() if valid_until_str else None

    db.session.commit()

    return jsonify({
        'message': 'Document metadata updated successfully',
        'document': {
            'id': document.id,
            'name': document.name,
            'document_type': document.document_type,
            'valid_from': document.valid_from.isoformat() if document.valid_from else None,
            'valid_until': document.valid_until.isoformat() if document.valid_until else None,
            'is_active': document.is_active
        }
    }), 200

# Маршрут для удаления документа
@documents_bp.route('/<string:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    file_manager.delete_file(document.file_path)

    db.session.delete(document)
    db.session.commit()

    return jsonify({'message': 'Document deleted successfully'}), 200

# Маршрут для пакетного скачивания документов (ПАКЕТНОЕ СКАЧИВАНИЕ С КИРИЛЛИЦЕЙ)
@documents_bp.route('/download_batch', methods=['POST'])
@jwt_required()
def download_batch_documents():
    data = request.get_json()
    reagent_ids = data.get('reagent_ids')

    if not isinstance(reagent_ids, list) or not reagent_ids:
        return jsonify({'message': 'List of reagent IDs is required'}), 400

    memory_file = io.BytesIO()

    # Python 3 по умолчанию отлично поддерживает UTF-8 имена внутри ZIP архива,
    # если передавать ему обычные юникод-строки
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for reagent_id in reagent_ids:
            reagent = Reagent.query.get(reagent_id)
            if not reagent:
                current_app.logger.warning(f"Reagent with ID {reagent_id} not found for batch download.")
                continue

            actual_documents = Document.query.filter(
                Document.reagent_id == reagent.id,
                Document.is_active == True,
                (Document.valid_until >= datetime.now().date()) | (Document.valid_until == None)
            ).all()

            if not actual_documents:
                continue

            # Используем русское название реагента для папки
            reagent_folder_name = sanitize_filename_cyrillic(reagent.name)

            for doc in actual_documents:
                full_file_path = os.path.join(current_app.root_path, doc.file_path)

                if os.path.exists(full_file_path):
                    original_file_name_on_disk = os.path.basename(doc.file_path)
                    file_extension = os.path.splitext(original_file_name_on_disk)[1]

                    # Используем русское название документа для файла внутри архива
                    doc_filename_in_zip = sanitize_filename_cyrillic(doc.name) + file_extension

                    # Составляем путь внутри ZIP-архива (РусскаяПапка/РусскийФайл.pdf)
                    zip_path = os.path.join(reagent_folder_name, doc_filename_in_zip)

                    zf.write(full_file_path, arcname=zip_path)

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='tender_documents.zip'
    )
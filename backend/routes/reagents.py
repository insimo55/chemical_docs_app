# backend/routes/reagents.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from datetime import datetime, date 
# Импортируем из нашего пакета backend
from .. import db
from ..models import Reagent, Document, User # Добавим User, чтобы использовать его в будущем, если понадобится

reagents_bp = Blueprint('reagents', __name__)

# Хелпер для получения самого раннего срока действия документов
def get_min_valid_until(reagent_id):
    today = date.today() # Получаем текущую дату через стандартный Python
    
    # Ищем актуальные документы для реагента
    actual_docs = Document.query.filter(
        Document.reagent_id == reagent_id,
        Document.is_active == True,
        (Document.valid_until >= today) | (Document.valid_until == None)
    ).all()

    if not actual_docs:
        return None, "No active documents" # Нет активных документов

    min_date = None
    all_expired = True

    for doc in actual_docs:
        if doc.valid_until:
            if doc.valid_until >= today: # Сравниваем напрямую
                all_expired = False
                if min_date is None or doc.valid_until < min_date:
                    min_date = doc.valid_until
        else: # Документ бессрочный, если valid_until = None
            all_expired = False

    if all_expired and min_date is None: 
        # Находим самый поздний просроченный для отображения
        expired_doc = Document.query.filter(
            Document.reagent_id == reagent_id,
            Document.is_active == True,
            Document.valid_until < today
        ).order_by(desc(Document.valid_until)).first()
        if expired_doc:
            return expired_doc.valid_until, "Expired" 
        return None, "No active documents" 
    elif all_expired and min_date is not None: 
        return min_date, "Expired" 
    elif min_date:
        if (min_date - today).days <= 30:
            return min_date, "Expires soon"
        return min_date, "Active"
    else: 
        return None, "Active (perpetual)"


# Маршрут для создания нового реагента
@reagents_bp.route('/', methods=['POST'])
@jwt_required()
def create_reagent():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    manufacturer = data.get('manufacturer')

    if not name:
        return jsonify({'message': 'Reagent name is required'}), 400

    new_reagent = Reagent(
        name=name,
        description=description,
        manufacturer=manufacturer
    )
    db.session.add(new_reagent)
    db.session.commit()

    return jsonify({
        'message': 'Reagent created successfully',
        'reagent': {
            'id': new_reagent.id,
            'name': new_reagent.name,
            'description': new_reagent.description,
            'manufacturer': new_reagent.manufacturer
        }
    }), 201

# Маршрут для получения списка всех реагентов
@reagents_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_reagents():
    reagents = Reagent.query.order_by(Reagent.name).all()
    reagents_data = []
    for reagent in reagents:
        min_date, status = get_min_valid_until(reagent.id)
        reagents_data.append({
            'id': reagent.id,
            'name': reagent.name,
            'description': reagent.description,
            'manufacturer': reagent.manufacturer,
            'status': reagent.status,
            'min_valid_until': min_date.isoformat() if min_date else None,
            'validity_status': status,
            'created_at': reagent.created_at.isoformat(),
            'updated_at': reagent.updated_at.isoformat()
        })
    return jsonify(reagents_data), 200

# Маршрут для получения реагента по ID
@reagents_bp.route('/<string:reagent_id>', methods=['GET'])
@jwt_required()
def get_reagent(reagent_id):
    reagent = Reagent.query.get(reagent_id)
    if not reagent:
        return jsonify({'message': 'Reagent not found'}), 404

    min_date, status = get_min_valid_until(reagent.id)

    # Получаем все документы для этого реагента
    documents = Document.query.filter_by(reagent_id=reagent.id).order_by(Document.name).all()
    documents_data = []
    for doc in documents:
        # Определяем статус для каждого документа
        doc_validity_status = "Unknown"
        if doc.valid_until:
            today = datetime.today().date()
            if doc.valid_until < today:
                doc_validity_status = "Expired"
            elif (doc.valid_until - today).days <= 30:
                doc_validity_status = "Expires soon"
            else:
                doc_validity_status = "Active"
        elif doc.valid_until is None: # Бессрочный документ
             doc_validity_status = "Active (perpetual)"

        documents_data.append({
            'id': doc.id,
            'name': doc.name,
            'document_type': doc.document_type,
            'file_path': doc.file_path, # Пока отдаем полный путь, но на фронте не будем его показывать
            'valid_from': doc.valid_from.isoformat() if doc.valid_from else None,
            'valid_until': doc.valid_until.isoformat() if doc.valid_until else None,
            'is_active': doc.is_active,
            'validity_status': doc_validity_status,
            'created_at': doc.created_at.isoformat(),
            'updated_at': doc.updated_at.isoformat()
        })

    return jsonify({
        'id': reagent.id,
        'name': reagent.name,
        'description': reagent.description,
        'manufacturer': reagent.manufacturer,
        'status': reagent.status,
        'min_valid_until': min_date.isoformat() if min_date else None,
        'validity_status': status,
        'created_at': reagent.created_at.isoformat(),
        'updated_at': reagent.updated_at.isoformat(),
        'documents': documents_data # Добавляем список документов
    }), 200

# Маршрут для обновления реагента
@reagents_bp.route('/<string:reagent_id>', methods=['PUT'])
@jwt_required()
def update_reagent(reagent_id):
    reagent = Reagent.query.get(reagent_id)
    if not reagent:
        return jsonify({'message': 'Reagent not found'}), 404

    data = request.get_json()
    reagent.name = data.get('name', reagent.name)
    reagent.description = data.get('description', reagent.description)
    reagent.manufacturer = data.get('manufacturer', reagent.manufacturer)
    reagent.status = data.get('status', reagent.status) # Позволяем менять статус

    db.session.commit()

    min_date, status = get_min_valid_until(reagent.id)

    return jsonify({
        'message': 'Reagent updated successfully',
        'reagent': {
            'id': reagent.id,
            'name': reagent.name,
            'description': reagent.description,
            'manufacturer': reagent.manufacturer,
            'status': reagent.status,
            'min_valid_until': min_date.isoformat() if min_date else None,
            'validity_status': status
        }
    }), 200

# Маршрут для удаления реагента
@reagents_bp.route('/<string:reagent_id>', methods=['DELETE'])
@jwt_required()
def delete_reagent(reagent_id):
    reagent = Reagent.query.get(reagent_id)
    if not reagent:
        return jsonify({'message': 'Reagent not found'}), 404

    # Каскадное удаление документов и файлов будет обработано SQLAlchemy (cascade="all, delete-orphan")
    # Дополнительно нужно удалить файлы с диска, это сделаем позже в file_manager.py
    # Пока просто удаляем реагент из БД
    db.session.delete(reagent)
    db.session.commit()

    return jsonify({'message': 'Reagent deleted successfully'}), 200
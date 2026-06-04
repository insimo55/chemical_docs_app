# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

# Импортируем из нашего пакета backend
from .. import db
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Оставляем этот эндпоинт для обратной совместимости / первой регистрации
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User with this username already exists'}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=4))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# ================= USER MANAGEMENT ENDPOINTS =================

# 1. Получение списка всех пользователей
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.order_by(User.username).all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    return jsonify(users_data), 200

# 2. Создание пользователя из панели управления
@auth_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User with this username already exists'}), 409

    if email and User.query.filter_by(email=email).first():
        return jsonify({'message': 'User with this email already exists'}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

# 3. Редактирование пользователя (смена имени, email, пароля)
@auth_bp.route('/users/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')
    new_password = data.get('password')

    if new_username and new_username != user.username:
        if User.query.filter_by(username=new_username).first():
            return jsonify({'message': 'Username already taken'}), 409
        user.username = new_username

    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({'message': 'Email already in use'}), 409
        user.email = new_email

    # Если передан пароль — меняем его
    if new_password:
        user.set_password(new_password)

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

# 4. Удаление пользователя
@auth_bp.route('/users/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    
    # Проверка: если в системе всего один пользователь, не разрешаем его удалять
    total_users = User.query.count()
    if total_users <= 1:
        return jsonify({'message': 'Cannot delete the last remaining user'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200
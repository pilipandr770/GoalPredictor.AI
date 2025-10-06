"""
API маршруты для аутентификации пользователей
"""
from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя
    """
    try:
        data = request.get_json()
        
        # Валидация
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        
        if not all([email, username, password]):
            return jsonify({
                'success': False,
                'error': 'Все поля обязательны'
            }), 400
        
        # Проверить существующих пользователей
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'error': 'Email уже зарегистрирован'
            }), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'error': 'Имя пользователя уже занято'
            }), 400
        
        # Создать пользователя
        user = User(
            email=email,
            username=username
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Автоматический вход
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Регистрация успешна',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_premium': user.is_premium,
                'is_admin': user.is_admin
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Вход пользователя
    """
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email и пароль обязательны'
            }), 400
        
        # Найти пользователя
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Неверный email или пароль'
            }), 401
        
        # Вход
        login_user(user, remember=True)
        
        # Обновить последний вход
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Вход выполнен успешно',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_premium': user.is_premium,
                'is_admin': user.is_admin
            }
        })
        
    except Exception as e:
        import traceback
        print("=" * 50)
        print("ОШИБКА ВХОДА:")
        print(str(e))
        print(traceback.format_exc())
        print("=" * 50)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Выход пользователя
    """
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Выход выполнен'
    })


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Получить информацию о текущем пользователе
    """
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_premium': current_user.is_premium,
            'daily_predictions_count': current_user.daily_predictions_count,
            'subscription_end': current_user.subscription_end.isoformat() if current_user.subscription_end else None
        }
    })


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """
    Проверить статус аутентификации
    """
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'is_premium': current_user.is_premium
        } if current_user.is_authenticated else None
    })

"""
API маршруты для администратора
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func

from models import User, UserPrediction, Subscription
from extensions import db

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Доступ запрещен. Требуются права администратора.'
            }), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/stats')
@admin_required
def get_stats():
    """
    Получить общую статистику системы
    """
    try:
        # Общее количество пользователей
        total_users = User.query.count()
        
        # Количество Premium пользователей
        premium_users = User.query.filter_by(is_premium=True).count()
        
        # Количество администраторов
        admin_users = User.query.filter_by(is_admin=True).count()
        
        # Общее количество прогнозов
        total_predictions = db.session.query(func.sum(User.daily_predictions_count)).scalar() or 0
        
        # Приблизительный доход (Premium пользователи * средняя цена)
        # Предполагаем $10/месяц за Premium
        estimated_revenue = premium_users * 10
        
        # Новые пользователи за последние 7 дней
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        
        # Активные пользователи (заходили за последние 7 дней)
        active_users = User.query.filter(User.last_login >= week_ago).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'premium_users': premium_users,
                'admin_users': admin_users,
                'free_users': total_users - premium_users - admin_users,
                'total_predictions': total_predictions,
                'estimated_revenue': estimated_revenue,
                'new_users_week': new_users_week,
                'active_users': active_users
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users')
@admin_required
def get_users():
    """
    Получить список всех пользователей
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Получить пользователей с пагинацией
        pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = []
        for user in pagination.items:
            users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_premium': user.is_premium,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'daily_predictions_count': user.daily_predictions_count,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None
            })
        
        return jsonify({
            'success': True,
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>')
@admin_required
def get_user(user_id):
    """
    Получить детальную информацию о пользователе
    """
    try:
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_premium': user.is_premium,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'subscription_id': user.subscription_id,
                'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None,
                'daily_predictions_count': user.daily_predictions_count,
                'last_prediction_date': user.last_prediction_date.isoformat() if user.last_prediction_date else None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/upgrade', methods=['POST'])
@admin_required
def upgrade_user_to_premium(user_id):
    """
    Обновить пользователя до Premium (ручное назначение администратором)
    """
    try:
        user = User.query.get_or_404(user_id)
        
        # Установить Premium на 1 год
        user.is_premium = True
        user.subscription_end = datetime.utcnow() + timedelta(days=365)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Пользователь {user.username} обновлен до Premium'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Удалить пользователя
    """
    try:
        user = User.query.get_or_404(user_id)
        
        # Нельзя удалить администратора
        if user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Невозможно удалить администратора'
            }), 400
        
        # Удалить связанные данные
        # UserPrediction.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Пользователь {user.username} удален'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """
    Активировать/деактивировать пользователя
    """
    try:
        user = User.query.get_or_404(user_id)
        
        if user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Невозможно изменить статус администратора'
            }), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Пользователь {user.username} {"активирован" if user.is_active else "деактивирован"}',
            'is_active': user.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/subscriptions')
@admin_required
def get_subscriptions():
    """
    Получить список всех подписок
    """
    try:
        # Получить пользователей с Premium подписками
        premium_users = User.query.filter_by(is_premium=True).order_by(User.created_at.desc()).all()
        
        subscriptions = []
        for user in premium_users:
            subscriptions.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'subscription_id': user.subscription_id,
                'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'is_active': user.subscription_end > datetime.utcnow() if user.subscription_end else True
            })
        
        return jsonify({
            'success': True,
            'subscriptions': subscriptions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/analytics/daily')
@admin_required
def get_daily_analytics():
    """
    Получить аналитику по дням
    """
    try:
        # Статистика за последние 30 дней
        days = 30
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Новые пользователи по дням
        new_users_by_day = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.date(User.created_at)
        ).all()
        
        analytics = {
            'new_users': [{'date': str(day.date), 'count': day.count} for day in new_users_by_day]
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

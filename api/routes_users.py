"""
API маршруты для управления пользователями
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime

from models import User, UserPrediction, Prediction
from extensions import db

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Получить профиль текущего пользователя
    """
    user = current_user
    
    # Статистика пользователя
    total_viewed = UserPrediction.query.filter_by(user_id=user.id).count()
    
    # Точность просмотренных прогнозов
    viewed_predictions = db.session.query(Prediction).join(
        UserPrediction,
        Prediction.id == UserPrediction.prediction_id
    ).filter(
        UserPrediction.user_id == user.id,
        Prediction.is_correct.isnot(None)
    ).all()
    
    correct_viewed = sum(1 for p in viewed_predictions if p.is_correct)
    accuracy = (correct_viewed / len(viewed_predictions) * 100) if viewed_predictions else 0
    
    return jsonify({
        'success': True,
        'profile': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_premium': user.is_premium,
            'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None,
            'created_at': user.created_at.isoformat(),
            'statistics': {
                'total_predictions_viewed': total_viewed,
                'predictions_accuracy': round(accuracy, 2),
                'daily_predictions_used': user.daily_predictions_count
            }
        }
    })


@users_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    Обновить профиль пользователя
    """
    try:
        data = request.get_json()
        user = current_user
        
        # Обновить имя пользователя
        if 'username' in data:
            new_username = data['username']
            
            # Проверить уникальность
            existing = User.query.filter(
                User.username == new_username,
                User.id != user.id
            ).first()
            
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Имя пользователя уже занято'
                }), 400
            
            user.username = new_username
        
        # Обновить email
        if 'email' in data:
            new_email = data['email']
            
            # Проверить уникальность
            existing = User.query.filter(
                User.email == new_email,
                User.id != user.id
            ).first()
            
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Email уже зарегистрирован'
                }), 400
            
            user.email = new_email
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Профиль обновлен',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Изменить пароль пользователя
    """
    try:
        data = request.get_json()
        user = current_user
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Необходимо указать старый и новый пароль'
            }), 400
        
        # Проверить старый пароль
        if not user.check_password(old_password):
            return jsonify({
                'success': False,
                'error': 'Неверный старый пароль'
            }), 401
        
        # Установить новый пароль
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Пароль изменен'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_bp.route('/history', methods=['GET'])
@login_required
def get_prediction_history():
    """
    Получить историю просмотренных прогнозов
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Получить историю
        history_query = db.session.query(
            Prediction,
            UserPrediction.viewed_at
        ).join(
            UserPrediction,
            Prediction.id == UserPrediction.prediction_id
        ).filter(
            UserPrediction.user_id == current_user.id
        ).order_by(
            UserPrediction.viewed_at.desc()
        )
        
        pagination = history_query.paginate(page=page, per_page=per_page)
        
        history = []
        for prediction, viewed_at in pagination.items:
            match = prediction.match
            
            history.append({
                'match': {
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'league': match.league,
                    'date': match.match_date.isoformat()
                },
                'prediction': {
                    'probability': prediction.probability,
                    'confidence': prediction.confidence,
                    'is_correct': prediction.is_correct,
                    'actual_result': prediction.actual_result
                },
                'viewed_at': viewed_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'history': history,
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


@users_bp.route('/limits', methods=['GET'])
@login_required
def get_user_limits():
    """
    Получить информацию о лимитах пользователя
    """
    from config import Config
    
    user = current_user
    
    max_predictions = (
        Config.PREMIUM_PREDICTIONS_PER_DAY
        if user.is_premium
        else Config.FREE_PREDICTIONS_PER_DAY
    )
    
    remaining = max_predictions - user.daily_predictions_count
    
    return jsonify({
        'success': True,
        'limits': {
            'is_premium': user.is_premium,
            'daily_predictions_used': user.daily_predictions_count,
            'daily_predictions_max': max_predictions,
            'daily_predictions_remaining': max(0, remaining),
            'can_view_more': user.can_view_prediction()
        }
    })

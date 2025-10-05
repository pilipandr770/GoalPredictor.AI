"""
API маршруты для управления подписками
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from services.stripe_service import StripeService
from app import db

subscriptions_bp = Blueprint('subscriptions', __name__)
stripe_service = StripeService()


@subscriptions_bp.route('/create-checkout', methods=['POST'])
@login_required
def create_checkout_session():
    """
    Создать сессию оплаты для подписки
    """
    try:
        data = request.get_json()
        plan_type = data.get('plan_type', 'monthly')
        
        if plan_type not in ['monthly', 'yearly']:
            return jsonify({
                'success': False,
                'error': 'Неверный тип плана'
            }), 400
        
        # Создать сессию Stripe
        session = stripe_service.create_checkout_session(
            current_user,
            plan_type=plan_type
        )
        
        return jsonify({
            'success': True,
            'session_id': session['session_id'],
            'url': session['url']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@subscriptions_bp.route('/success', methods=['POST'])
@login_required
def handle_success():
    """
    Обработать успешную оплату
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID не указан'
            }), 400
        
        # Обработать платеж
        result = stripe_service.handle_successful_payment(session_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Подписка активирована!'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Ошибка активации подписки')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@subscriptions_bp.route('/info', methods=['GET'])
@login_required
def get_subscription_info():
    """
    Получить информацию о подписке пользователя
    """
    try:
        info = stripe_service.get_subscription_info(current_user)
        
        return jsonify({
            'success': True,
            'subscription': info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@subscriptions_bp.route('/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    """
    Отменить подписку
    """
    try:
        result = stripe_service.cancel_subscription(current_user)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@subscriptions_bp.route('/reactivate', methods=['POST'])
@login_required
def reactivate_subscription():
    """
    Возобновить отмененную подписку
    """
    try:
        result = stripe_service.reactivate_subscription(current_user)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@subscriptions_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Webhook для обработки событий Stripe
    """
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    try:
        result = stripe_service.handle_webhook(payload, signature)
        
        if result['success']:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@subscriptions_bp.route('/plans', methods=['GET'])
def get_plans():
    """
    Получить доступные планы подписки
    """
    plans = [
        {
            'id': 'monthly',
            'name': 'Monthly Premium',
            'price': 9.99,
            'currency': 'EUR',
            'interval': 'month',
            'features': [
                'Неограниченные прогнозы',
                'Детальная аналитика',
                'Приоритетная поддержка',
                'Email уведомления'
            ]
        },
        {
            'id': 'yearly',
            'name': 'Yearly Premium',
            'price': 99.99,
            'currency': 'EUR',
            'interval': 'year',
            'features': [
                'Все возможности Monthly',
                'Скидка 17%',
                'Ранний доступ к новым функциям',
                'Персональные консультации'
            ],
            'popular': True
        }
    ]
    
    return jsonify({
        'success': True,
        'plans': plans
    })

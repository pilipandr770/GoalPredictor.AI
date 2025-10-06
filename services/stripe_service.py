"""
Сервис для работы с платежами и подписками через Stripe
"""
import stripe
from datetime import datetime, timedelta
from config import Config
from models import User, Subscription
from extensions import db


class StripeService:
    """
    Клиент для Stripe API
    """
    
    def __init__(self):
        stripe.api_key = Config.STRIPE_SECRET_KEY
        self.public_key = Config.STRIPE_PUBLIC_KEY
        self.monthly_price_id = Config.STRIPE_PRICE_ID_MONTHLY
        self.yearly_price_id = Config.STRIPE_PRICE_ID_YEARLY
    
    def create_checkout_session(self, user, plan_type='monthly', success_url=None, cancel_url=None):
        """
        Создать сессию оплаты для подписки
        
        Args:
            user: Объект пользователя
            plan_type: 'monthly' или 'yearly'
            success_url: URL для успешной оплаты
            cancel_url: URL для отмены
        
        Returns:
            dict: Данные сессии Stripe
        """
        if success_url is None:
            success_url = f"{Config.APP_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        
        if cancel_url is None:
            cancel_url = f"{Config.APP_URL}/subscription/cancel"
        
        # Выбрать Price ID в зависимости от плана
        price_id = self.monthly_price_id if plan_type == 'monthly' else self.yearly_price_id
        
        try:
            # Создать или получить Stripe Customer
            customer = self._get_or_create_customer(user)
            
            # Создать Checkout Session
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': user.id,
                    'plan_type': plan_type
                }
            )
            
            return {
                'session_id': session.id,
                'url': session.url,
                'public_key': self.public_key
            }
            
        except stripe.error.StripeError as e:
            print(f"❌ Stripe ошибка: {e}")
            raise Exception(f"Не удалось создать сессию оплаты: {str(e)}")
    
    def _get_or_create_customer(self, user):
        """
        Получить или создать Stripe Customer для пользователя
        """
        # Проверить есть ли уже customer
        subscriptions = Subscription.query.filter_by(user_id=user.id).first()
        
        if subscriptions and subscriptions.stripe_customer_id:
            try:
                customer = stripe.Customer.retrieve(subscriptions.stripe_customer_id)
                return customer
            except stripe.error.StripeError:
                pass
        
        # Создать нового customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.username,
            metadata={
                'user_id': user.id
            }
        )
        
        return customer
    
    def handle_successful_payment(self, session_id):
        """
        Обработать успешную оплату
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != 'paid':
                return {'success': False, 'error': 'Оплата не подтверждена'}
            
            # Получить подписку
            subscription_id = session.subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Получить пользователя
            user_id = int(session.metadata.get('user_id'))
            user = User.query.get(user_id)
            
            if not user:
                return {'success': False, 'error': 'Пользователь не найден'}
            
            # Создать запись подписки в БД
            self._create_subscription_record(user, subscription, session.metadata.get('plan_type'))
            
            return {'success': True, 'user_id': user_id}
            
        except stripe.error.StripeError as e:
            print(f"❌ Ошибка обработки платежа: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_subscription_record(self, user, stripe_subscription, plan_type):
        """
        Создать запись подписки в базе данных
        """
        # Проверить существующую подписку
        existing_sub = Subscription.query.filter_by(user_id=user.id, status='active').first()
        
        if existing_sub:
            # Отменить старую подписку
            existing_sub.status = 'canceled'
            existing_sub.canceled_at = datetime.utcnow()
        
        # Создать новую подписку
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=stripe_subscription.customer,
            stripe_price_id=stripe_subscription.items.data[0].price.id,
            status=stripe_subscription.status,
            plan_type=plan_type,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end)
        )
        
        db.session.add(subscription)
        
        # Обновить статус пользователя
        user.is_premium = True
        user.subscription_id = stripe_subscription.id
        user.subscription_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        
        db.session.commit()
        
        print(f"✅ Подписка создана для пользователя {user.id}")
    
    def cancel_subscription(self, user):
        """
        Отменить подписку пользователя
        """
        subscription = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if not subscription:
            return {'success': False, 'error': 'Активная подписка не найдена'}
        
        try:
            # Отменить подписку в Stripe (в конце периода)
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            # Обновить в БД
            subscription.cancel_at = subscription.current_period_end
            db.session.commit()
            
            return {'success': True, 'message': 'Подписка будет отменена в конце периода'}
            
        except stripe.error.StripeError as e:
            print(f"❌ Ошибка отмены подписки: {e}")
            return {'success': False, 'error': str(e)}
    
    def reactivate_subscription(self, user):
        """
        Возобновить отмененную подписку
        """
        subscription = Subscription.query.filter_by(user_id=user.id).first()
        
        if not subscription:
            return {'success': False, 'error': 'Подписка не найдена'}
        
        try:
            # Отменить запланированную отмену
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False
            )
            
            subscription.cancel_at = None
            db.session.commit()
            
            return {'success': True, 'message': 'Подписка возобновлена'}
            
        except stripe.error.StripeError as e:
            print(f"❌ Ошибка возобновления подписки: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_webhook(self, payload, signature):
        """
        Обработать webhook от Stripe
        
        Webhooks нужны для автоматического обновления статуса подписок
        """
        webhook_secret = Config.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
        except ValueError:
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError:
            return {'success': False, 'error': 'Invalid signature'}
        
        # Обработать различные типы событий
        event_type = event['type']
        
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            self.handle_successful_payment(session['id'])
        
        elif event_type == 'invoice.paid':
            # Успешное продление подписки
            invoice = event['data']['object']
            self._handle_invoice_paid(invoice)
        
        elif event_type == 'invoice.payment_failed':
            # Неудачная попытка оплаты
            invoice = event['data']['object']
            self._handle_payment_failed(invoice)
        
        elif event_type == 'customer.subscription.deleted':
            # Подписка удалена
            subscription = event['data']['object']
            self._handle_subscription_deleted(subscription)
        
        return {'success': True}
    
    def _handle_invoice_paid(self, invoice):
        """Обработать успешную оплату счета"""
        subscription_id = invoice['subscription']
        
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()
        
        if subscription:
            # Обновить период подписки
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_sub.current_period_end
            )
            subscription.status = 'active'
            
            # Обновить пользователя
            subscription.user.subscription_end = subscription.current_period_end
            subscription.user.is_premium = True
            
            db.session.commit()
            print(f"✅ Подписка продлена для пользователя {subscription.user_id}")
    
    def _handle_payment_failed(self, invoice):
        """Обработать неудачную оплату"""
        subscription_id = invoice['subscription']
        
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()
        
        if subscription:
            subscription.status = 'past_due'
            db.session.commit()
            print(f"⚠️ Неудачная оплата для пользователя {subscription.user_id}")
    
    def _handle_subscription_deleted(self, stripe_subscription):
        """Обработать удаление подписки"""
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=stripe_subscription['id']
        ).first()
        
        if subscription:
            subscription.status = 'canceled'
            subscription.canceled_at = datetime.utcnow()
            
            # Обновить пользователя
            subscription.user.is_premium = False
            subscription.user.subscription_id = None
            subscription.user.subscription_end = None
            
            db.session.commit()
            print(f"❌ Подписка отменена для пользователя {subscription.user_id}")
    
    def get_subscription_info(self, user):
        """
        Получить информацию о подписке пользователя
        """
        subscription = Subscription.query.filter_by(
            user_id=user.id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            return {
                'has_subscription': False,
                'is_premium': False
            }
        
        return {
            'has_subscription': True,
            'is_premium': user.is_premium,
            'status': subscription.status,
            'plan_type': subscription.plan_type,
            'current_period_end': subscription.current_period_end.isoformat(),
            'cancel_at': subscription.cancel_at.isoformat() if subscription.cancel_at else None,
            'will_cancel': subscription.cancel_at is not None
        }


if __name__ == '__main__':
    print("🔐 Stripe Service инициализирован")
    print("⚠️  Для тестирования используйте тестовые карты Stripe:")
    print("   Успешная оплата: 4242 4242 4242 4242")
    print("   Неудачная оплата: 4000 0000 0000 0002")

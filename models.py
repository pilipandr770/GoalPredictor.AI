"""
Модели базы данных для GoalPredictor.AI
"""
import os
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'
    __table_args__ = {'schema': os.getenv('DATABASE_SCHEMA', 'goalpredictor')}
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Роль пользователя
    is_admin = db.Column(db.Boolean, default=False)
    
    # Подписка
    is_premium = db.Column(db.Boolean, default=False)
    subscription_id = db.Column(db.String(255), nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    
    # Статистика использования
    daily_predictions_count = db.Column(db.Integer, default=0)
    last_prediction_date = db.Column(db.Date, nullable=True)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Связи
    predictions = db.relationship('UserPrediction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Установить хэш пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password_hash, password)
    
    def can_view_prediction(self):
        """Проверка, может ли пользователь просмотреть прогноз"""
        # Сброс счетчика если новый день
        if self.last_prediction_date != datetime.utcnow().date():
            self.daily_predictions_count = 0
            self.last_prediction_date = datetime.utcnow().date()
            db.session.commit()
        
        if self.is_premium:
            return True
        
        from config import Config
        return self.daily_predictions_count < Config.FREE_PREDICTIONS_PER_DAY
    
    def increment_prediction_count(self):
        """Увеличить счетчик просмотренных прогнозов"""
        if self.last_prediction_date != datetime.utcnow().date():
            self.daily_predictions_count = 1
            self.last_prediction_date = datetime.utcnow().date()
        else:
            self.daily_predictions_count += 1
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'


class Team(db.Model):
    """Модель команды"""
    __tablename__ = 'teams'
    __table_args__ = {'schema': os.getenv('DATABASE_SCHEMA', 'goalpredictor')}
    
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    league = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    
    # Статистика
    total_matches = db.Column(db.Integer, default=0)
    goals_scored = db.Column(db.Integer, default=0)
    goals_conceded = db.Column(db.Integer, default=0)
    avg_goals_per_match = db.Column(db.Float, default=0.0)
    over_2_5_percentage = db.Column(db.Float, default=0.0)
    
    # Форма (последние матчи)
    last_5_form = db.Column(db.String(5), nullable=True)  # WWDLL
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Team {self.name}>'


class Match(db.Model):
    """Модель матча"""
    __tablename__ = 'matches'
    __table_args__ = {'schema': os.getenv('DATABASE_SCHEMA', 'goalpredictor')}
    
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    
    # Команды
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    
    # Информация о матче
    league = db.Column(db.String(50), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, finished
    
    # Результаты (заполняются после матча)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    home_goals = db.Column(db.Integer, nullable=True)  # Alias для home_score
    away_goals = db.Column(db.Integer, nullable=True)  # Alias для away_score
    total_goals = db.Column(db.Integer, nullable=True)
    
    # Дополнительные результаты для анализа
    result = db.Column(db.String(1), nullable=True)  # '1' (home win), 'X' (draw), '2' (away win)
    over_2_5 = db.Column(db.Boolean, nullable=True)  # Тотал больше 2.5
    btts = db.Column(db.Boolean, nullable=True)  # Обе команды забили (Both Teams To Score)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    predictions = db.relationship('Prediction', backref='match', lazy='dynamic')
    
    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name}>'


class Prediction(db.Model):
    """Модель прогноза"""
    __tablename__ = 'predictions'
    __table_args__ = {'schema': os.getenv('DATABASE_SCHEMA', 'goalpredictor')}
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    
    # Прогноз
    prediction_type = db.Column(db.String(50), default='over_2.5')  # over_2.5, btts, etc.
    probability = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.String(20), nullable=False)  # high, medium, low
    
    # Объяснение (от OpenAI)
    explanation = db.Column(db.Text, nullable=True)
    factors = db.Column(db.JSON, nullable=True)  # Ключевые факторы в JSON
    
    # Результат
    is_correct = db.Column(db.Boolean, nullable=True)  # Заполняется после матча
    actual_result = db.Column(db.String(50), nullable=True)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<Prediction {self.prediction_type} - {self.probability:.2%}>'


class UserPrediction(db.Model):
    """История просмотров прогнозов пользователем"""
    __tablename__ = 'user_predictions'
    __table_args__ = {'schema': os.getenv('DATABASE_SCHEMA', 'goalpredictor')}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    prediction = db.relationship('Prediction', backref='user_views')


class Subscription(db.Model):
    """Модель подписки"""
    __tablename__ = 'subscriptions'
    __table_args__ = {'schema': os.getenv('DATABASE_SCHEMA', 'goalpredictor')}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Stripe данные
    stripe_subscription_id = db.Column(db.String(255), unique=True, nullable=False)
    stripe_customer_id = db.Column(db.String(255), nullable=False)
    stripe_price_id = db.Column(db.String(255), nullable=False)
    
    # Статус
    status = db.Column(db.String(50), nullable=False)  # active, canceled, past_due
    plan_type = db.Column(db.String(20), nullable=False)  # monthly, yearly
    
    # Даты
    current_period_start = db.Column(db.DateTime, nullable=False)
    current_period_end = db.Column(db.DateTime, nullable=False)
    cancel_at = db.Column(db.DateTime, nullable=True)
    canceled_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь
    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Subscription {self.stripe_subscription_id} - {self.status}>'

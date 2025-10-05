"""
Конфигурация приложения GoalPredictor.AI
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Базовая конфигурация"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///goalpredictor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # API Keys - Football API
    FOOTBALL_API_PROVIDER = os.getenv('FOOTBALL_API_PROVIDER', 'football-data-org')
    
    # football-data.org
    FOOTBALL_DATA_ORG_KEY = os.getenv('FOOTBALL_DATA_ORG_KEY')
    
    # RapidAPI (альтернатива)
    FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')
    FOOTBALL_API_HOST = os.getenv('FOOTBALL_API_HOST', 'api-football-v1.p.rapidapi.com')
    FOOTBALL_API_BASE_URL = os.getenv('FOOTBALL_API_BASE_URL', 'https://api-football-v1.p.rapidapi.com/v3')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    
    # Stripe
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    STRIPE_PRICE_ID_MONTHLY = os.getenv('STRIPE_PRICE_ID_MONTHLY')
    STRIPE_PRICE_ID_YEARLY = os.getenv('STRIPE_PRICE_ID_YEARLY')
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@goalpredictor.ai')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'GoalPredictor.AI')
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Leagues (Top 5 European Leagues)
    # Для football-data.org используем коды типа 'PL', 'PD' и т.д.
    # Для RapidAPI используем числовые ID
    LEAGUES = {
        'Premier League': os.getenv('LEAGUE_ID_PREMIER_LEAGUE', 'PL'),
        'La Liga': os.getenv('LEAGUE_ID_LA_LIGA', 'PD'),
        'Bundesliga': os.getenv('LEAGUE_ID_BUNDESLIGA', 'BL1'),
        'Serie A': os.getenv('LEAGUE_ID_SERIE_A', 'SA'),
        'Ligue 1': os.getenv('LEAGUE_ID_LIGUE_1', 'FL1')
    }
    
    # ML Model Settings
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'models')
    MODEL_RETRAIN_DAYS = int(os.getenv('MODEL_RETRAIN_DAYS', 7))
    PREDICTION_THRESHOLD = float(os.getenv('PREDICTION_THRESHOLD', 0.65))
    MIN_MATCHES_FOR_PREDICTION = int(os.getenv('MIN_MATCHES_FOR_PREDICTION', 5))
    
    # Subscription Limits
    FREE_PREDICTIONS_PER_DAY = int(os.getenv('FREE_PREDICTIONS_PER_DAY', 3))
    PREMIUM_PREDICTIONS_PER_DAY = int(os.getenv('PREMIUM_PREDICTIONS_PER_DAY', 999))
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CORS
    CORS_HEADERS = 'Content-Type'


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    # В продакшене обязательно использовать PostgreSQL
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Выбор конфигурации на основе переменной окружения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

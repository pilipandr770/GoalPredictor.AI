"""
GoalPredictor.AI - Flask Application
Аналитическая платформа для прогнозирования футбольных матчей
"""
import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name=None):
    """
    Фабрика приложений Flask
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)
    
    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    
    # Импорт моделей базы данных
    with app.app_context():
        from models import User, Prediction, Match, Team, Subscription
        db.create_all()
    
    # Регистрация blueprints (API маршрутов)
    from api.routes_matches import matches_bp
    from api.routes_users import users_bp
    from api.routes_subscriptions import subscriptions_bp
    from api.routes_auth import auth_bp
    
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Основные маршруты
    @app.route('/')
    def index():
        """Главная страница"""
        return render_template('index.html')
    
    @app.route('/predictions')
    def predictions():
        """Страница прогнозов"""
        return render_template('predictions.html')
    
    @app.route('/about')
    def about():
        """О проекте"""
        return render_template('about.html')
    
    @app.route('/pricing')
    def pricing():
        """Тарифы и подписки"""
        return render_template('pricing.html')
    
    @app.route('/profile')
    def profile():
        """Профиль пользователя"""
        return render_template('profile.html')
    
    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Страница не найдена'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
    
    # Здоровье приложения
    @app.route('/health')
    def health():
        """Проверка состояния приложения"""
        return jsonify({
            'status': 'healthy',
            'app': app.config['APP_NAME'],
            'version': '1.0.0'
        })
    
    return app


# Загрузка пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app = create_app()
    
    # Запуск планировщика задач в отдельном потоке
    from services.scheduler import start_scheduler
    start_scheduler(app)
    
    # Запуск Flask приложения
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

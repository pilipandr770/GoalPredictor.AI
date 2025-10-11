"""
GoalPredictor.AI - Flask Application
Аналитическая платформа для прогнозирования футбольных матчей
"""
import os
from flask import Flask, render_template, jsonify, request, redirect
from flask_cors import CORS
from config import config
from extensions import db, migrate, login_manager


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
    login_manager.login_view = 'login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    
    # Загрузка пользователя для Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Импорт моделей базы данных
    with app.app_context():
        from models import User, Prediction, Match, Team, Subscription
        db.create_all()
    
    # Регистрация blueprints (API маршрутов)
    from api.routes_matches import matches_bp
    from api.routes_users import users_bp
    from api.routes_subscriptions import subscriptions_bp
    from api.routes_auth import auth_bp
    from api.routes_admin import admin_bp
    from api.routes_tennis import tennis_bp  # 🎾 Tennis routes
    from api.routes_football import football_bp  # ⚽ Football routes
    
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(tennis_bp)  # 🎾 /api/tennis/*
    app.register_blueprint(football_bp)  # ⚽ /api/football/*
    
    # Инициализация tennis prediction service при старте
    with app.app_context():
        from tennis.predict import get_tennis_prediction_service
        tennis_service = get_tennis_prediction_service()
        print(f"🎾 Tennis prediction service initialized")
    
    # API эндпоинты для прогнозов
    @app.route('/api/predictions/upcoming')
    def get_upcoming_predictions():
        """Получить прогнозы для предстоящих матчей"""
        from services.prediction_service import get_prediction_service
        
        try:
            service = get_prediction_service()
            days = request.args.get('days', 7, type=int)
            
            # Получить расписание
            upcoming_matches = service.get_upcoming_matches(days_ahead=days)
            
            # Добавить прогнозы
            predictions = []
            for match in upcoming_matches[:20]:  # Ограничение на 20 матчей
                prediction = service.predict_match(match)
                predictions.append({
                    'match': match,
                    'prediction': prediction
                })
            
            return jsonify({
                'success': True,
                'count': len(predictions),
                'predictions': predictions
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/predictions/match/<int:match_id>')
    def get_match_prediction(match_id):
        """Получить детальный прогноз для конкретного матча"""
        from services.prediction_service import get_prediction_service
        
        try:
            service = get_prediction_service()
            
            # Получить информацию о матче
            # (В реальности нужно получить из БД или API)
            match_info = {
                'id': match_id,
                'home_team_id': 123,
                'away_team_id': 456,
                'date': '2024-10-10 15:00'
            }
            
            prediction = service.predict_match(match_info)
            
            return jsonify({
                'success': True,
                'prediction': prediction
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
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
    
    @app.route('/tennis')
    def tennis():
        """Страница прогнозов тенниса"""
        return render_template('tennis.html')
    
    @app.route('/football')
    def football():
        """Страница прогнозов футбола"""
        from datetime import datetime
        return render_template('football.html', now=datetime.now().strftime('%H:%M:%S'))
    
    @app.route('/football-test')
    def football_test():
        """Тестовая страница для отладки Football API"""
        return render_template('football_test.html')
    
    @app.route('/test-simple')
    def test_simple():
        """Простейший тест JavaScript"""
        return render_template('test_simple.html')
    
    @app.route('/profile')
    def profile():
        """Профиль пользователя"""
        return render_template('profile.html')
    
    @app.route('/impressum')
    def impressum():
        """Impressum - Контактная информация"""
        return render_template('impressum.html')
    
    @app.route('/datenschutz')
    def datenschutz():
        """Datenschutz - Защита данных"""
        return render_template('datenschutz.html')
    
    @app.route('/agb')
    def agb():
        """AGB - Общие условия использования"""
        return render_template('agb.html')
    
    # Обработчики ошибок
    # Веб-маршруты для HTML страниц
    @app.route('/login')
    def login_page():
        """Страница входа"""
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """Страница регистрации"""
        return render_template('register.html')
    
    @app.route('/admin')
    def admin_page():
        """Админ-панель (требуется аутентификация)"""
        from flask_login import current_user
        if not current_user.is_authenticated:
            return redirect('/login')
        if not current_user.is_admin:
            return "Доступ запрещен", 403
        return render_template('admin/dashboard.html')
    
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


# Создание глобального экземпляра приложения для Gunicorn
app = create_app()


if __name__ == '__main__':
    # Запуск планировщика задач в отдельном потоке
    from services.scheduler import start_scheduler
    start_scheduler(app)
    
    # Запуск Flask приложения
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

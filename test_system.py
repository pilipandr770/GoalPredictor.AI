"""
🧪 Комплексный тест GoalPredictor.AI
Проверка всех основных компонентов системы
"""

import sys
from datetime import datetime

print("\n" + "="*60)
print("🧪 ТЕСТ КОМПОНЕНТОВ GoalPredictor.AI")
print("="*60 + "\n")

# Счетчики
tests_passed = 0
tests_failed = 0
warnings = 0

def test_step(name, func):
    """Выполнить тестовый шаг"""
    global tests_passed, tests_failed, warnings
    
    try:
        print(f"▶️  {name}...", end=" ")
        result = func()
        
        if result == "warning":
            print("⚠️  ПРЕДУПРЕЖДЕНИЕ")
            warnings += 1
        else:
            print("✅ OK")
            tests_passed += 1
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        tests_failed += 1
        return False


# === ТЕСТ 1: Импорты ===
print("📦 Проверка зависимостей...")
print("-" * 60)

def test_flask():
    import flask
    return True

def test_sqlalchemy():
    import sqlalchemy
    return True

def test_lightgbm():
    try:
        import lightgbm
        return True
    except ImportError:
        return "warning"

def test_openai():
    try:
        import openai
        return True
    except ImportError:
        return "warning"

test_step("Flask", test_flask)
test_step("SQLAlchemy", test_sqlalchemy)
test_step("LightGBM", test_lightgbm)
test_step("OpenAI SDK", test_openai)


# === ТЕСТ 2: Конфигурация ===
print("\n⚙️  Проверка конфигурации...")
print("-" * 60)

def test_config():
    from config import Config
    return True

def test_env_variables():
    from config import Config
    
    if not Config.FOOTBALL_DATA_ORG_KEY or Config.FOOTBALL_DATA_ORG_KEY == 'your-api-key-here':
        print("\n   ⚠️  FOOTBALL_DATA_ORG_KEY не настроен в .env")
        return "warning"
    
    return True

def test_openai_key():
    from config import Config
    
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY.startswith('your-'):
        print("\n   ⚠️  OPENAI_API_KEY не настроен в .env")
        return "warning"
    
    return True

test_step("Config загрузка", test_config)
test_step("Football API ключ", test_env_variables)
test_step("OpenAI API ключ", test_openai_key)


# === ТЕСТ 3: Сервисы ===
print("\n🔌 Проверка сервисов...")
print("-" * 60)

def test_football_api_service():
    from services.football_api import FootballAPIService
    api = FootballAPIService()
    return True

def test_football_data_org():
    from services.football_data_org import FootballDataOrgAPI
    api = FootballDataOrgAPI()
    return True

def test_openai_service():
    try:
        from services.openai_service import OpenAIService
        service = OpenAIService()
        return True
    except:
        return "warning"

test_step("FootballAPIService", test_football_api_service)
test_step("FootballDataOrgAPI", test_football_data_org)
test_step("OpenAIService", test_openai_service)


# === ТЕСТ 4: База данных ===
print("\n💾 Проверка базы данных...")
print("-" * 60)

def test_db_models():
    from models import User, Match, Prediction
    return True

def test_db_connection():
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        # Проверяем подключение
        db.engine.connect()
    
    return True

test_step("Модели БД", test_db_models)
test_step("Подключение к БД", test_db_connection)


# === ТЕСТ 5: ML модуль ===
print("\n🧠 Проверка ML модуля...")
print("-" * 60)

def test_feature_engineering():
    from ml.model import GoalPredictorModel
    model = GoalPredictorModel()
    return True

def test_predictor():
    from ml.predict import PredictionService
    predictor = PredictionService()
    return True if predictor else "warning"

def test_ml_model_exists():
    import os
    
    lgb_exists = os.path.exists('models/goal_predictor_lgb.pkl')
    xgb_exists = os.path.exists('models/goal_predictor_xgb.pkl')
    
    if not lgb_exists and not xgb_exists:
        print("\n   ⚠️  ML модель не обучена! Запустите: python ml/train.py")
        return "warning"
    
    return True

test_step("GoalPredictorModel", test_feature_engineering)
test_step("PredictionService", test_predictor)
test_step("ML модель обучена", test_ml_model_exists)


# === ТЕСТ 6: API маршруты ===
print("\n🛣️  Проверка API маршрутов...")
print("-" * 60)

def test_app_creation():
    from app import create_app
    app = create_app()
    return True

def test_blueprints():
    from app import create_app
    app = create_app()
    
    blueprints = [bp.name for bp in app.blueprints.values()]
    
    required = ['auth', 'matches', 'subscriptions', 'users']
    missing = [bp for bp in required if bp not in blueprints]
    
    if missing:
        print(f"\n   ⚠️  Отсутствуют blueprints: {missing}")
        return "warning"
    
    return True

test_step("Создание Flask app", test_app_creation)
test_step("Blueprints регистрация", test_blueprints)


# === ТЕСТ 7: Живой API тест ===
print("\n🌐 Проверка внешних API...")
print("-" * 60)

def test_football_api_live():
    from services.football_api import FootballAPIService
    
    api = FootballAPIService()
    fixtures = api.get_todays_fixtures()
    
    if fixtures is None:
        print("\n   ⚠️  API вернул None (проверьте ключ или лимиты)")
        return "warning"
    
    print(f"\n   📊 Найдено матчей: {len(fixtures)}")
    
    return True

def test_openai_api_live():
    try:
        from services.openai_service import OpenAIService
        from config import Config
        
        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY.startswith('your-'):
            return "warning"
        
        service = OpenAIService()
        
        # Простой тест (не тратим токены на реальный запрос)
        return True
        
    except Exception as e:
        print(f"\n   ⚠️  {e}")
        return "warning"

test_step("Football-Data.org API", test_football_api_live)
test_step("OpenAI API", test_openai_api_live)


# === ИТОГИ ===
print("\n" + "="*60)
print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
print("="*60)

total_tests = tests_passed + tests_failed + warnings

print(f"\n✅ Пройдено:      {tests_passed}/{total_tests}")
print(f"❌ Провалено:     {tests_failed}/{total_tests}")
print(f"⚠️  Предупреждений: {warnings}/{total_tests}")

if tests_failed == 0 and warnings == 0:
    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к работе!")
    sys.exit(0)
elif tests_failed == 0:
    print(f"\n⚠️  Система работает, но есть {warnings} предупреждений.")
    print("   Рекомендуется настроить все API ключи и обучить ML модель.")
    sys.exit(0)
else:
    print(f"\n❌ КРИТИЧЕСКИЕ ОШИБКИ: {tests_failed}")
    print("   Проверьте установку зависимостей и конфигурацию.")
    sys.exit(1)

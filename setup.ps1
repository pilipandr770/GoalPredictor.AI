# GoalPredictor.AI - Setup Script
# Первоначальная настройка проекта

Write-Host "⚽ GoalPredictor.AI - Настройка проекта" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# 1. Создание виртуального окружения
Write-Host "1️⃣  Создание виртуального окружения..." -ForegroundColor Cyan
if (Test-Path "venv") {
    Write-Host "   ✓ Виртуальное окружение уже существует" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "   ✓ Виртуальное окружение создано" -ForegroundColor Green
}

# 2. Активация окружения
Write-Host ""
Write-Host "2️⃣  Активация окружения..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1
Write-Host "   ✓ Окружение активировано" -ForegroundColor Green

# 3. Обновление pip
Write-Host ""
Write-Host "3️⃣  Обновление pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet
Write-Host "   ✓ pip обновлен" -ForegroundColor Green

# 4. Установка зависимостей
Write-Host ""
Write-Host "4️⃣  Установка зависимостей (это может занять несколько минут)..." -ForegroundColor Cyan
pip install -r requirements.txt
Write-Host "   ✓ Зависимости установлены" -ForegroundColor Green

# 5. Создание .env файла
Write-Host ""
Write-Host "5️⃣  Настройка переменных окружения..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "   ✓ Файл .env уже существует" -ForegroundColor Green
} else {
    Copy-Item .env.example .env
    Write-Host "   ✓ Файл .env создан из .env.example" -ForegroundColor Green
    Write-Host "   ⚠️  ВАЖНО: Заполните API ключи в файле .env!" -ForegroundColor Yellow
}

# 6. Создание директорий
Write-Host ""
Write-Host "6️⃣  Создание необходимых директорий..." -ForegroundColor Cyan
$directories = @("data", "ml/models", "static/images", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "   ✓ Директории созданы" -ForegroundColor Green

# 7. Инициализация базы данных
Write-Host ""
Write-Host "7️⃣  Инициализация базы данных..." -ForegroundColor Cyan
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('   ✓ База данных создана')"

# Финальные инструкции
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host "✅ Настройка завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Следующие шаги:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Откройте файл .env и заполните API ключи:" -ForegroundColor Yellow
Write-Host "   - FOOTBALL_API_KEY (получите на rapidapi.com)" -ForegroundColor Gray
Write-Host "   - OPENAI_API_KEY (получите на platform.openai.com)" -ForegroundColor Gray
Write-Host "   - STRIPE_SECRET_KEY (получите на stripe.com)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Скачайте датасет с Kaggle и поместите в data/football_matches.csv" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Обучите ML-модель:" -ForegroundColor Yellow
Write-Host "   python ml\train.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Запустите приложение:" -ForegroundColor Yellow
Write-Host "   .\run.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Документация: README.md" -ForegroundColor Cyan
Write-Host "🐛 Проблемы: https://github.com/your-repo/issues" -ForegroundColor Cyan
Write-Host ""

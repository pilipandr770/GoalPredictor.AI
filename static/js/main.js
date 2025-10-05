// GoalPredictor.AI - Основной JavaScript

// Модальное окно входа
function showLoginModal() {
    // TODO: Реализовать модальное окно
    window.location.href = '/login';
}

// Загрузка прогнозов
async function loadPredictions(league = null) {
    try {
        const url = league ? `/api/matches/today?league=${league}` : '/api/matches/today';
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            return data.predictions;
        } else {
            console.error('Ошибка загрузки прогнозов:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Ошибка запроса:', error);
        return [];
    }
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        day: 'numeric', 
        month: 'long', 
        hour: '2-digit', 
        minute: '2-digit' 
    };
    return date.toLocaleDateString('ru-RU', options);
}

// Копирование в буфер обмена
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Скопировано в буфер обмена', 'success');
    }).catch(err => {
        console.error('Ошибка копирования:', err);
    });
}

// Уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Аутентификация
async function login(email, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Вход выполнен успешно!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Ошибка входа', 'error');
        }
    } catch (error) {
        console.error('Ошибка входа:', error);
        showNotification('Ошибка соединения', 'error');
    }
}

async function register(email, username, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Регистрация успешна!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.error || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        console.error('Ошибка регистрации:', error);
        showNotification('Ошибка соединения', 'error');
    }
}

// Подписка
async function createCheckoutSession(planType) {
    try {
        const response = await fetch('/api/subscriptions/create-checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ plan_type: planType })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Перенаправить на Stripe Checkout
            window.location.href = data.url;
        } else {
            showNotification(data.error || 'Ошибка создания сессии', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка соединения', 'error');
    }
}

// Отмена подписки
async function cancelSubscription() {
    if (!confirm('Вы уверены, что хотите отменить подписку?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/subscriptions/cancel', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification(data.error || 'Ошибка отмены подписки', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка соединения', 'error');
    }
}

// Экспорт функций для использования в HTML
window.GoalPredictor = {
    loadPredictions,
    formatDate,
    copyToClipboard,
    showNotification,
    login,
    register,
    createCheckoutSession,
    cancelSubscription
};

console.log('✅ GoalPredictor.AI загружен');

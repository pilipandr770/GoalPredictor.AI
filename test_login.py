"""
Тестовый скрипт для проверки логина
"""
import requests
import json

# Тестируем логин
url = "http://127.0.0.1:5000/api/auth/login"
data = {
    "email": "admin@goalpredictor.ai",
    "password": "admin123"
}

print("Отправка запроса на логин...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Ошибка: {e}")

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔧 ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ С ПРАВИЛЬНЫМИ ЗАГОЛОВКАМИ")
    print("=" * 60)
    
    # 1. Логинимся
    print("1. 🔑 Выполняем вход...")
    login_data = {
        "username": "test@example.com",
        "password": "test123"
    }
    
    response = requests.post(
        f"{BASE_URL}/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Ошибка логина: {response.status_code}")
        print(f"   Ответ: {response.text}")
        return
    
    token_data = response.json()
    token = token_data.get("access_token")
    
    if not token:
        print("   ❌ Токен не получен!")
        print(f"   Ответ: {token_data}")
        return
    
    print(f"   ✅ Токен получен: {token[:50]}...")
    
    print("\n" + "=" * 60)
    print("2. 🛡️ Тестируем запросы с заголовком Authorization")
    print("-" * 60)
    
    # Правильные заголовки
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2.1. /users/me
    print("a) GET /users/me")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"   Статус: {response.status_code}")
    print(f"   Заголовки запроса: Authorization: Bearer {token[:20]}...")
    
    if response.status_code == 200:
        print(f"   ✅ Успех! Ответ: {response.json()}")
    else:
        print(f"   ❌ Ошибка: {response.text}")
    
    # 2.2. /tests/available
    print("\nb) GET /tests/available")
    response = requests.get(f"{BASE_URL}/tests/available", headers=headers)
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Успех! Тестов: {len(data)}")
    else:
        print(f"   ❌ Ошибка: {response.text}")
    
    # 2.3. /tests/my-results
    print("\nc) GET /tests/my-results")
    response = requests.get(f"{BASE_URL}/tests/my-results", headers=headers)
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Успех! Результатов: {len(data)}")
    else:
        print(f"   ℹ️ Ответ: {response.text}")
    
    print("\n" + "=" * 60)
    print("3. 🚫 Тестируем запросы БЕЗ заголовка (ожидаем 401)")
    print("-" * 60)
    
    # Без заголовка
    response = requests.get(f"{BASE_URL}/users/me")
    print(f"   GET /users/me без заголовка: {response.status_code}")
    
    if response.status_code == 401:
        print("   ✅ Корректно: 401 без токена")
    else:
        print(f"   ❌ Неожиданно: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 ВАЖНО: После логина ВСЕГДА добавляйте заголовок:")
    print(f"   Authorization: Bearer {token[:50]}...")
    print("=" * 60)

if __name__ == "__main__":
    main()

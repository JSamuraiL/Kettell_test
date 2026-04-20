import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
import hashlib

def hash_password(password: str) -> str:
    """Простое хеширование SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    db = SessionLocal()
    try:
        # Список тестовых пользователей
        test_users = [
            {
                "email": "test@example.com",
                "password": "test123",
                "full_name": "Test User",
                "role": "user"
            },
            {
                "email": "psychologist@example.com",
                "password": "psy123",
                "full_name": "Dr. Psychologist",
                "role": "psychologist"
            },
            {
                "email": "admin@example.com",
                "password": "admin123",
                "full_name": "Admin User",
                "role": "admin"
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            # Проверяем, есть ли уже пользователь
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"User {user_data['email']} already exists")
                continue
            
            # Создаем нового пользователя
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"]
            )
            
            db.add(user)
            created_count += 1
            print(f"Created user: {user_data['email']} / {user_data['password']}")
        
        db.commit()
        print(f"\nCreated {created_count} test users")
        
        # Показать созданных пользователей
        print("\nTest users created:")
        print("1. test@example.com / test123 (user)")
        print("2. psychologist@example.com / psy123 (psychologist)")
        print("3. admin@example.com / admin123 (admin)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()

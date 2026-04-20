import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def create_psychologist():
    db = SessionLocal()
    
    psychologist_data = {
        "email": "psychologist@test.com",
        "full_name": "Тестовый Психолог",
        "role": "psychologist",
        "password": "psychologist123"
    }
    
    # Проверяем, существует ли уже такой пользователь
    existing_user = db.query(User).filter(User.email == psychologist_data["email"]).first()
    if existing_user:
        print(f"Пользователь с email {psychologist_data['email']} уже существует")
        db.close()
        return
    
    # Создаем нового пользователя
    new_user = User(
        email=psychologist_data["email"],
        hashed_password=get_password_hash(psychologist_data["password"]),
        full_name=psychologist_data["full_name"],
        role=psychologist_data["role"],
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ Психолог создан успешно!")
    print(f"   Email: {new_user.email}")
    print(f"   Имя: {new_user.full_name}")
    print(f"   Роль: {new_user.role}")
    print(f"   ID: {new_user.id}")
    print(f"   Код для привязки: PSY-{new_user.id}")
    
    db.close()

if __name__ == "__main__":
    create_psychologist()


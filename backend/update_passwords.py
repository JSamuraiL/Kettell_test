import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash
import hashlib

def hash_password(password: str) -> str:
    """Простое хеширование SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def update_user_passwords():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        updated_count = 0
        
        for user in users:
            print(f"Checking user: {user.email}")
            print(f"Current password hash: {user.hashed_password}")
            print(f"Length: {len(user.hashed_password) if user.hashed_password else 0}")
            
            # Если пароль хранится в открытом виде (не похоже на SHA256 хеш)
            if user.hashed_password and len(user.hashed_password) != 64:  # SHA256 hash имеет 64 символа
                print(f"  Updating password for user: {user.email}")
                # Перехешируем пароль
                user.hashed_password = hash_password(user.hashed_password)
                updated_count += 1
            else:
                print(f"  Password already hashed for user: {user.email}")
        
        db.commit()
        print(f"\nUpdated {updated_count} users out of {len(users)}")
        
        # Показать обновленные данные
        print("\nUpdated users:")
        for user in users:
            print(f"  {user.email}: {user.hashed_password[:20]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_passwords()

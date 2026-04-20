import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base

def reset_database():
    print("Пересоздание базы данных...")
    
    try:
        # Удаляем все таблицы
        Base.metadata.drop_all(bind=engine)
        print("✅ Старые таблицы удалены")
        
        # Создаем новые таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ Новые таблицы созданы")
        
        print("\n🎉 База данных успешно пересоздана!")
        print("\nСозданные таблицы:")
        for table in Base.metadata.tables.values():
            print(f"  - {table.name}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    confirm = input("Вы уверены, что хотите пересоздать базу данных? Все данные будут удалены! (yes/no): ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Отменено")

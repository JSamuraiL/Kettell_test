import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import Base

def init_database():
    print("Инициализация базы данных...")
    
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы успешно созданы")
        
        # Показать созданные таблицы
        print("\nСозданные таблицы:")
        for table in Base.metadata.tables.values():
            print(f"  - {table.name}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_database()

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from sqlalchemy import inspect, text

def check_database_structure():
    print("Проверка структуры базы данных...")
    
    # Создаем инспектор для проверки структуры
    inspector = inspect(engine)
    
    print("\nТаблицы в базе данных:")
    tables = inspector.get_table_names()
    for table in tables:
        print(f"\nТаблица: {table}")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']}: {column['type']}")
    
    # Проверяем конкретно таблицу test_results
    if 'test_results' in tables:
        print("\n\nПроверка таблицы test_results:")
        columns = inspector.get_columns('test_results')
        column_names = [col['name'] for col in columns]
        print(f"Колонки: {column_names}")
        
        # Какие колонки ожидаются
        expected_columns = [
            'id', 'user_id', 'test_part', 'raw_score_a', 'raw_score_b',
            'total_raw_score', 'age_at_test', 'age_group', 'standard_score',
            'percentile', 'completed_at', 'answers', 'time_spent', 'interpretation'
        ]
        
        print("\nОтсутствующие колонки:")
        for expected in expected_columns:
            if expected not in column_names:
                print(f"  ❌ {expected}")
            else:
                print(f"  ✅ {expected}")
    
    print("\n" + "="*50)
    
    # Проверка через SQL
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version();"))
        print(f"PostgreSQL версия: {result.fetchone()[0]}")
        
        result = db.execute(text("SELECT current_database();"))
        print(f"Текущая база: {result.fetchone()[0]}")
        
        db.close()
    except Exception as e:
        print(f"Ошибка при проверке: {e}")

if __name__ == "__main__":
    check_database_structure()

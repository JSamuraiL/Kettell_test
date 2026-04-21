import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Test, Question, NormativeData
from datetime import datetime

def create_test_data():
    db = SessionLocal()
    try:
        print("Создание тестовых данных...")
        
        # 1. Создаем тесты (часть A)
        test_a1 = Test(
            test_part="A",
            test_number=1,
            name="Тест A1: Серии",
            description_image="/static/images/test_a1_desc.png",
            instruction_text="Выберите фигуру, которая продолжает ряд",
            time_limit=180,
            is_active=True
        )
        
        test_a2 = Test(
            test_part="A",
            test_number=2,
            name="Тест A2: Классификация",
            description_image="/static/images/test_a2_desc.png",
            instruction_text="Выберите фигуру, которая отличается от других",
            time_limit=150,
            is_active=True
        )
        
        test_b1 = Test(
            test_part="B",
            test_number=1,
            name="Тест B1: Матрицы",
            description_image="/static/images/test_b1_desc.png",
            instruction_text="Выберите фигуру, которая подходит на место вопроса",
            time_limit=200,
            is_active=True
        )
        
        test_b2 = Test(
            test_part="B",
            test_number=2,
            name="Тест B2: Топология",
            description_image="/static/images/test_b2_desc.png",
            instruction_text="Выберите правильное расположение фигур",
            time_limit=180,
            is_active=True
        )
        
        db.add_all([test_a1, test_a2, test_b1, test_b2])
        db.flush()  # Получаем ID
        
        print(f"Создано 4 теста")
        
        # 2. Создаем вопросы для теста A1
        questions_a1 = []
        for i in range(1, 14):  # 13 вопросов для теста A1
            question = Question(
                test_id=test_a1.id,
                question_number=i,
                image_path=f"/static/images/test_a1_q{i}.png",
                correct_answer="b" if i % 3 == 0 else "a",  # Пример правильных ответов
                difficulty_level=1 if i <= 4 else (2 if i <= 8 else 3)
            )
            questions_a1.append(question)
        
        # Вопросы для теста A2
        questions_a2 = []
        for i in range(1, 14):
            question = Question(
                test_id=test_a2.id,
                question_number=i,
                image_path=f"/static/images/test_a2_q{i}.png",
                correct_answer="c" if i % 4 == 0 else "a",
                difficulty_level=1 if i <= 4 else (2 if i <= 8 else 3)
            )
            questions_a2.append(question)
        
        db.add_all(questions_a1 + questions_a2)
        print(f"Создано {len(questions_a1 + questions_a2)} вопросов")
        
        # 3. Нормативные данные в БД (сида для разработки)
        normative_data = []
        age_groups = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        
        for age_group in age_groups:
            for raw_score in range(0, 51, 5):  # От 0 до 50 с шагом 5
                normative = NormativeData(
                    age_group=age_group,
                    raw_score_min=raw_score,
                    raw_score_max=raw_score + 4,
                    iq_score=90 + raw_score * 2,
                    percentile=min(99, max(1, raw_score * 2)),
                    description=f"Уровень для возрастной группы {age_group}"
                )
                normative_data.append(normative)
        
        db.add_all(normative_data)
        print(f"Создано {len(normative_data)} нормативных записей")
        
        db.commit()
        print("✅ Тестовые данные успешно созданы!")
        
        # Показать созданные данные
        tests = db.query(Test).all()
        print(f"\nВсего тестов в БД: {len(tests)}")
        for test in tests:
            question_count = db.query(Question).filter(Question.test_id == test.id).count()
            print(f"  {test.test_part}{test.test_number}: {test.name} ({question_count} вопросов)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()

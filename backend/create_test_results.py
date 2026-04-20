import sys
import os
import random
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, Test, TestResult, Question
from datetime import datetime, timedelta

def create_test_results():
    db = SessionLocal()
    try:
        print("Создание тестовых результатов...")
        
        # Находим пользователя
        user = db.query(User).filter(User.email == "newuser@example.com").first()
        if not user:
            print("Пользователь не найден, используем первого пользователя")
            user = db.query(User).first()
        
        if not user:
            print("Нет пользователей в БД!")
            return
        
        print(f"Создаем результаты для пользователя: {user.email}")
        
        # Находим тесты
        tests = db.query(Test).all()
        if not tests:
            print("Нет тестов в БД!")
            return
        
        # Создаем результаты для каждого теста
        for test in tests:
            # Находим вопросы этого теста
            questions = db.query(Question).filter(Question.test_id == test.id).all()
            
            if not questions:
                continue
            
            # Создаем "ответы" пользователя
            answers = []
            for q in questions:
                # Случайный ответ (иногда правильный)
                if random.random() > 0.3:  # 70% правильных ответов
                    answer = q.correct_answer
                    is_correct = True
                else:
                    # Случайный неправильный ответ
                    answer = random.choice(['a', 'b', 'c', 'd', 'e'])
                    is_correct = (answer == q.correct_answer)
                
                answers.append({
                    "question_id": q.id,
                    "answer": answer,
                    "time_spent": random.uniform(5, 30)  # 5-30 секунд на вопрос
                })
            
            # Рассчитываем сырой балл (количество правильных ответов)
            correct_answers = sum(1 for a in answers if a["answer"] == q.correct_answer)
            
            # Рассчитываем IQ (упрощенная формула)
            base_iq = 100 + (correct_answers - len(questions)/2) * 3
            
            # Создаем результат теста
            test_result = TestResult(
                user_id=user.id,
                test_part=test.test_part,
                raw_score_a=correct_answers if test.test_part == 'A' else None,
                raw_score_b=correct_answers if test.test_part == 'B' else None,
                total_raw_score=correct_answers,
                age_at_test=25,  # Примерный возраст
                age_group="25-34",
                standard_score=round(base_iq, 1),
                percentile=min(99, max(1, int((base_iq - 70) / 60 * 98))),
                answers=answers,
                time_spent=int(sum(a["time_spent"] for a in answers)),
                interpretation="Средний уровень интеллекта. Норма для большинства людей.",
                completed_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            
            db.add(test_result)
            print(f"  Создан результат для теста {test.test_part}{test.test_number}: {correct_answers}/{len(questions)} правильных ответов, IQ: {round(base_iq, 1)}")
        
        db.commit()
        print(f"\n✅ Создано {len(tests)} тестовых результатов!")
        
        # Показать статистику
        results = db.query(TestResult).filter(TestResult.user_id == user.id).all()
        print(f"\nВсего результатов у пользователя: {len(results)}")
        for r in results:
            print(f"  Тест {r.test_part}: {r.total_raw_score} баллов, IQ: {r.standard_score}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_results()

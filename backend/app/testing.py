from sqlalchemy.orm import Session
from datetime import date
import json
from typing import Dict, List, Optional
from . import models, schemas
from .answer_keys import get_correct_answer
from . import normative_tables

class TestingService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_age(self, user_id: int) -> int:
        """Получить возраст пользователя"""
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user or not user.date_of_birth:
            return 25  # значение по умолчанию
        return schemas.calculate_age(user.date_of_birth)
    
    def get_age_group(self, age: int) -> str:
        """Получить возрастную группу"""
        return schemas.get_age_group(age)
    
    def get_tests_by_part(self, test_part: str) -> List[models.Test]:
        """Получить все тесты для указанной части"""
        return self.db.query(models.Test).filter(
            models.Test.test_part == test_part,
            models.Test.is_active == True
        ).order_by(models.Test.test_number).all()
    
    def get_questions_by_test(self, test_id: int) -> List[models.Question]:
        """Получить все вопросы для теста"""
        return self.db.query(models.Question).filter(
            models.Question.test_id == test_id
        ).order_by(models.Question.question_number).all()
    
    def calculate_raw_score(self, answers: List[schemas.TestAnswer], test_id: int) -> int:
        """Рассчитать сырой балл за тест на основе ключа и БД"""
        test = self.db.query(models.Test).filter(models.Test.id == test_id).first()
        if not test:
            return 0

        score = 0
        for answer in answers:
            if answer.answer == "skip":
                continue

            question = self.db.query(models.Question).filter(
                models.Question.id == answer.question_id,
                models.Question.test_id == test_id
            ).first()

            if not question:
                continue

            # Предпочитаем ключ из предоставленного файла, если он есть
            key_answer = get_correct_answer(
                test_part=test.test_part,
                test_number=test.test_number,
                question_number=question.question_number,
            )

            correct_answer = key_answer or question.correct_answer

            if correct_answer and answer.answer == correct_answer:
                score += 1

        return score
    
    def _percentile_from_iq(self, iq: float) -> int:
        if iq < 70: return 2
        if iq < 85: return 16
        if iq < 100: return 50
        if iq < 115: return 84
        if iq < 130: return 98
        return 99

    def _interpret_iq(self, iq: float) -> str:
        if iq < 70:
            return "Ниже 70: существенно ниже среднего уровня."
        if iq < 90:
            return "70–89: ниже среднего уровня."
        if iq <= 110:
            return "90–110: средний уровень."
        if iq <= 119:
            return "111–119: выше среднего."
        if iq <= 129:
            return "120–129: высокий уровень."
        return "130+: очень высокий уровень."

    def calculate_iq_score(self, raw_score: int, age: int, test_part: str = 'full') -> Dict:
        """
        Рассчитать IQ на основе сырого балла и возраста.
        Сначала пытаемся взять таблицу нормативов (из файла пользователя),
        затем — fallback на старую формулу.
        """
        # Пробуем нормативную таблицу
        norm_result = normative_tables.get_iq_by_age(raw_score, age)
        if norm_result:
            iq, age_group_label = norm_result
            interpretation = self._interpret_iq(iq)
            return {
                'standard_score': iq,
                'percentile': self._percentile_from_iq(iq),
                'interpretation': interpretation,
                'age_group': age_group_label,
            }

        # Fallback на старую формулу
        age_group = self.get_age_group(age)
        if test_part == 'A':
            base_iq = 100 + (raw_score - 25) * 2
        elif test_part == 'B':
            base_iq = 100 + (raw_score - 23) * 2
        else:  # full
            base_iq = 100 + (raw_score - 48) * 1.5
        
        age_factor = {
            '18-24': 1.0, '25-34': 1.05, '35-44': 1.0,
            '45-54': 0.95, '55-64': 0.9, '65+': 0.85
        }
        
        iq = base_iq * age_factor.get(age_group, 1.0)
        
        if iq < 70: percentile = 2
        elif iq < 85: percentile = 16
        elif iq < 100: percentile = 50
        elif iq < 115: percentile = 84
        elif iq < 130: percentile = 98
        else: percentile = 99
        
        if iq < 70:
            interpretation = "Значительно ниже среднего. Рекомендуется консультация специалиста."
        elif iq < 85:
            interpretation = "Ниже среднего. Есть потенциал для развития."
        elif iq < 100:
            interpretation = "Средний уровень. Норма для большинства людей."
        elif iq < 115:
            interpretation = "Выше среднего. Хорошие интеллектуальные способности."
        elif iq < 130:
            interpretation = "Высокий уровень. Отличные интеллектуальные способности."
        else:
            interpretation = "Очень высокий уровень. Выдающиеся интеллектуальные способности."
        
        return {
            'standard_score': round(iq, 1),
            'percentile': percentile,
            'interpretation': interpretation,
            'age_group': age_group,
        }
    
    def save_test_result(
        self,
        user_id: int,
        test_part: str,
        answers: List[schemas.TestAnswer],
        test_id: int,
        time_spent: int
    ) -> models.TestResult:
        """Сохранить результаты теста"""
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        age = self.get_user_age(user_id)
        age_group = self.get_age_group(age)
        
        raw_score = self.calculate_raw_score(answers, test_id)
        
        # Сохраняем результат теста без финального IQ (он будет после полного прохода)
        test_result = models.TestResult(
            user_id=user_id,
            test_part=test_part,
            raw_score_a=raw_score if test_part == 'A' else None,
            raw_score_b=raw_score if test_part == 'B' else None,
            total_raw_score=raw_score,
            age_at_test=age,
            age_group=age_group,
            standard_score=None,
            percentile=None,
            time_spent=time_spent,
            answers=[answer.dict() for answer in answers],
            interpretation=None
        )
        
        self.db.add(test_result)
        self.db.flush()  # Получаем ID для связи
        
        # Сохраняем ответы на каждый вопрос
        test = self.db.query(models.Test).filter(models.Test.id == test_id).first()
        for answer in answers:
            question = self.db.query(models.Question).filter(
                models.Question.id == answer.question_id
            ).first()
            
            is_correct = False
            if question and answer.answer != 'skip':
                # Используем правильный ключ ответов из answer_keys.py
                key_answer = get_correct_answer(
                    test_part=test.test_part,
                    test_number=test.test_number,
                    question_number=question.question_number,
                )
                correct_answer = key_answer or question.correct_answer
                is_correct = (answer.answer == correct_answer)
            
            user_answer = models.UserAnswer(
                test_result_id=test_result.id,
                question_id=answer.question_id,
                user_answer=answer.answer,
                is_correct=is_correct,
                time_spent=answer.time_spent
            )
            
            self.db.add(user_answer)
        
        self.db.commit()
        self.db.refresh(test_result)

        # После коммита проверяем, прошёл ли пользователь все тесты.
        total_tests = self.db.query(models.Test).filter(models.Test.is_active == True).count()
        completed_test_ids = set(
            t[0] for t in self.db.query(models.Question.test_id)
            .join(models.UserAnswer, models.UserAnswer.question_id == models.Question.id)
            .join(models.TestResult, models.TestResult.id == models.UserAnswer.test_result_id)
            .filter(models.TestResult.user_id == user_id)
            .distinct()
            .all()
        )

        if total_tests > 0 and len(completed_test_ids) == total_tests:
            # Подсчитываем общий сырой балл, суммируя правильные ответы из всех тестов
            # Используем UserAnswer для точного подсчета правильных ответов
            all_user_answers = (
                self.db.query(models.UserAnswer)
                .join(models.TestResult, models.UserAnswer.test_result_id == models.TestResult.id)
                .filter(models.TestResult.user_id == user_id)
                .all()
            )
            
            # Пересчитываем правильность ответов с использованием правильных ключей
            total_raw = 0
            for ua in all_user_answers:
                question = self.db.query(models.Question).filter(
                    models.Question.id == ua.question_id
                ).first()
                
                if question and ua.user_answer != 'skip':
                    test_for_question = self.db.query(models.Test).filter(
                        models.Test.id == question.test_id
                    ).first()
                    
                    if test_for_question:
                        key_answer = get_correct_answer(
                            test_part=test_for_question.test_part,
                            test_number=test_for_question.test_number,
                            question_number=question.question_number,
                        )
                        correct_answer = key_answer or question.correct_answer
                        
                        if ua.user_answer == correct_answer:
                            total_raw += 1
                            # Обновляем is_correct в базе данных
                            ua.is_correct = True
                        else:
                            ua.is_correct = False
            
            # Сохраняем изменения is_correct перед расчетом IQ
            self.db.commit()

            iq_data = self.calculate_iq_score(total_raw, age, test_part='full')

            # Обновляем все результаты этим финальным IQ и общей суммой
            all_results = self.db.query(models.TestResult).filter(
                models.TestResult.user_id == user_id
            ).all()
            
            for r in all_results:
                r.total_raw_score = total_raw
                r.standard_score = iq_data['standard_score']
                r.percentile = iq_data['percentile']
                r.interpretation = iq_data['interpretation']
                r.age_group = iq_data.get('age_group', r.age_group)
                r.test_part = 'full'  # Помечаем как полное тестирование
            
            self.db.commit()
            self.db.refresh(test_result)
        
        return test_result

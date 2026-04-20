from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # Колонка в БД называется hashed_password (исторически). 
    # Атрибут в модели — hashed_password.
    hashed_password = Column("hashed_password", String, nullable=False)
    full_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    role = Column(String, default="user")  # 'user' или 'psychologist'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    psychologist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Простые связи
    psychologist = relationship("User", remote_side=[id], backref="patients")
    test_results = relationship("TestResult", back_populates="user")

# Модель для тестов (части A и B)
class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_part = Column(String)  # 'A' или 'B'
    test_number = Column(Integer)  # 1-4 для каждой части
    name = Column(String)  # Название теста
    description_image = Column(String)  # Путь к картинке с описанием
    instruction_text = Column(Text)  # Текст инструкции
    time_limit = Column(Integer)  # Лимит времени в секундах
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    questions = relationship("Question", back_populates="test")

# Модель для вопросов
class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    question_number = Column(Integer)  # Номер вопроса в тесте
    image_path = Column(String)  # Путь к картинке вопроса
    correct_answer = Column(String)  # 'a', 'b', 'c', 'd', 'e'
    difficulty_level = Column(Integer, default=1)  # Уровень сложности 1-3
    
    # Связи
    test = relationship("Test", back_populates="questions")

# Модель для нормативных данных (конвертация баллов в IQ)
class NormativeData(Base):
    __tablename__ = "normative_data"
    
    id = Column(Integer, primary_key=True, index=True)
    age_group = Column(String)  # Возрастная группа, напр. '18-24'
    raw_score_min = Column(Integer)  # Минимальный сырой балл для этой группы
    raw_score_max = Column(Integer)  # Максимальный сырой балл для этой группы
    iq_score = Column(Float)  # Соответствующий IQ
    percentile = Column(Integer)  # Процентиль
    description = Column(Text)  # Описание интерпретации

# Модель для результатов теста
class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_part = Column(String)  # 'A', 'B' или 'full' (A+B) - ЭТОТ СТОЛБЕЦ ДОЛЖЕН БЫТЬ!
    raw_score_a = Column(Integer)  # Сырой балл по части A
    raw_score_b = Column(Integer)  # Сырой балл по части B
    total_raw_score = Column(Integer)  # Общий сырой балл
    age_at_test = Column(Integer)  # Возраст на момент тестирования
    age_group = Column(String)  # Возрастная группа
    standard_score = Column(Float)  # Стандартизированный балл (IQ)
    percentile = Column(Integer)  # Процентиль
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    answers = Column(JSON)  # JSON со всеми ответами пользователя
    time_spent = Column(Integer)  # Общее время в секундах
    interpretation = Column(Text)  # Текст интерпретации
    
    # Связи
    user = relationship("User", back_populates="test_results")

# Модель для ответов пользователя на вопросы
class UserAnswer(Base):
    __tablename__ = "user_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    test_result_id = Column(Integer, ForeignKey("test_results.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String) # 'a', 'b', 'c', 'd', 'e' или 'skip'
    is_correct = Column(Boolean)
    time_spent = Column(Float)  # Время на вопрос в секундах
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    test_result = relationship("TestResult")
    question = relationship("Question")

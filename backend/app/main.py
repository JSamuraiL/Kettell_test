from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional, Set
import re
from fastapi.staticfiles import StaticFiles

from app import models, schemas, auth
from app.database import get_db, engine
from app.config import settings
from app.testing import TestingService

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Culture Fair Intelligence Test")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="static/images"), name="images")

# CORS настройки для React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Лимиты времени по субтестам: A1-3 по 4 минуты, остальные по 3
TIME_LIMITS = {
    ("A", 1): 240,
    ("A", 2): 240,
    ("A", 3): 240,
}


def get_time_limit(test: models.Test) -> int:
    return TIME_LIMITS.get((test.test_part, test.test_number), test.time_limit or 180)

# Зависимость для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = auth.verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Регистрация
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем, нет ли уже пользователя с таким email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Логин
@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Поддержка старых учетных записей с незахешированными паролями
    legacy_plain_password = (
        user.hashed_password 
        and len(user.hashed_password) != 64 
        and user.hashed_password == form_data.password
    )
    
    password_ok = auth.verify_password(form_data.password, user.hashed_password)
    
    if not password_ok and legacy_plain_password:
        # Обновляем пароль до хеша, чтобы дальнейшие входы работали корректно
        user.hashed_password = auth.get_password_hash(form_data.password)
        db.commit()
        db.refresh(user)
        password_ok = True
    
    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# Получение текущего пользователя
@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Эндпоинт для привязки психолога
@app.post("/psychologist/link")
def link_psychologist(
    link_data: schemas.PsychologistLink,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Привязать психолога к пользователю"""
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can link to psychologists"
        )
    
    psychologist = None
    
    if link_data.psychologist_code:
        # Извлекаем ID из кода формата "PSY-2"
        try:
            if link_data.psychologist_code.startswith("PSY-"):
                psychologist_id = int(link_data.psychologist_code.split("-")[1])
            else:
                psychologist_id = int(link_data.psychologist_code)
            
            psychologist = db.query(models.User).filter(
                models.User.role == "psychologist",
                models.User.id == psychologist_id
            ).first()
        except (ValueError, IndexError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid psychologist code format. Use 'PSY-{id}' or just the ID number."
            )
    
    elif link_data.psychologist_email:
        psychologist = db.query(models.User).filter(
            models.User.role == "psychologist",
            models.User.email == link_data.psychologist_email
        ).first()
    
    if not psychologist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Psychologist not found"
        )
    
    current_user.psychologist_id = psychologist.id
    db.commit()
    
    return {
        "message": "Psychologist linked successfully", 
        "psychologist": {
            "id": psychologist.id,
            "email": psychologist.email,
            "full_name": psychologist.full_name,
            "code": f"PSY-{psychologist.id}"
        }
    }

# Для психолога: получить своих пациентов
@app.get("/psychologist/patients", response_model=List[schemas.UserWithTests])
def get_my_patients(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Психолог получает список своих пациентов"""
    if current_user.role != "psychologist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can view patients"
        )
    
    patients = db.query(models.User).filter(
        models.User.psychologist_id == current_user.id,
        models.User.role == "user"
    ).all()
    
    result = []
    for patient in patients:
        test_count = db.query(models.TestResult).filter(
            models.TestResult.user_id == patient.id
        ).count()
        
        last_test = db.query(models.TestResult).filter(
            models.TestResult.user_id == patient.id
        ).order_by(models.TestResult.completed_at.desc()).first()
        
        result.append({
            "id": patient.id,
            "email": patient.email,
            "full_name": patient.full_name,
            "test_count": test_count,
            "last_test_date": last_test.completed_at if last_test else None
        })
    
    return result

# Для психолога: получить результаты тестов пациента
@app.get("/psychologist/patient/{patient_id}/results", response_model=List[schemas.TestResultResponse])
def get_patient_results(
    patient_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Психолог получает полные результаты тестов пациента"""
    if current_user.role != "psychologist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can view patient results"
        )
    
    # Проверяем, что пациент привязан к этому психологу
    patient = db.query(models.User).filter(
        models.User.id == patient_id,
        models.User.psychologist_id == current_user.id,
        models.User.role == "user"
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not linked to you"
        )
    
    # Проверяем, что пройдены все активные тесты
    total_tests = db.query(models.Test).filter(models.Test.is_active == True).count()
    completed_test_ids = set(
        t[0] for t in db.query(models.Question.test_id)
        .join(models.UserAnswer, models.UserAnswer.question_id == models.Question.id)
        .join(models.TestResult, models.TestResult.id == models.UserAnswer.test_result_id)
        .filter(models.TestResult.user_id == patient_id)
        .distinct()
        .all()
    )

    if total_tests == 0 or len(completed_test_ids) < total_tests:
        # Не показываем частичные результаты психологу
        return []

    # Ищем результат с test_part='full' (общий результат тестирования)
    # Если его нет, берем самый последний результат, который должен иметь общий IQ
    full_result = db.query(models.TestResult).filter(
        models.TestResult.user_id == patient_id,
        models.TestResult.test_part == 'full'
    ).order_by(models.TestResult.completed_at.desc()).first()
    
    if not full_result:
        # Если нет результата с test_part='full', берем последний результат
        # который должен иметь общий IQ после прохождения всех тестов
        full_result = db.query(models.TestResult).filter(
            models.TestResult.user_id == patient_id,
            models.TestResult.standard_score.isnot(None)
        ).order_by(models.TestResult.completed_at.desc()).first()
    
    if not full_result:
        return []
    
    # Очищаем текст "Возрастная норма" и остаточные числа из интерпретации, если они есть
    if full_result.interpretation:
        # Убираем текст "Возрастная норма: ..." из интерпретации
        full_result.interpretation = re.sub(
            r'\s*Возрастная норма:?\s*[^.]*\.?',
            '',
            full_result.interpretation
        )
        # Убираем остаточные числа в формате "X-Y.Z." или "X-Y.Z" в конце строки
        full_result.interpretation = re.sub(
            r'\s*\d+\.?\d*[-–]\d+\.?\d*\.?\s*$',
            '',
            full_result.interpretation
        ).strip()
    
    # Возвращаем один общий результат тестирования
    return [full_result]

# Получить информацию о тестах
@app.get("/tests/available", response_model=List[schemas.TestInfo])
def get_available_tests(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список доступных тестов"""
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can take tests"
        )
    
    tests = db.query(models.Test).filter(
        models.Test.is_active == True
    ).order_by(models.Test.test_part, models.Test.test_number).all()

    # Определяем уже пройденные тесты пользователем
    completed_ids: Set[int] = set(
        t[0] for t in db.query(models.Question.test_id)
        .join(models.UserAnswer, models.UserAnswer.question_id == models.Question.id)
        .join(models.TestResult, models.UserAnswer.test_result_id == models.TestResult.id)
        .filter(models.TestResult.user_id == current_user.id)
        .distinct()
        .all()
    )
    
    result = []
    for test in tests:
        question_count = db.query(models.Question).filter(
            models.Question.test_id == test.id
        ).count()
        
        result.append({
            **test.__dict__,
            'question_count': question_count,
            'time_limit': get_time_limit(test),
            'completed': test.id in completed_ids
        })
    
    return result

# Начать тест - получить вопросы
@app.get("/tests/{test_id}/questions", response_model=List[schemas.QuestionResponse])
def get_test_questions(
    test_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить вопросы для теста"""
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can take tests"
        )
    
    questions = db.query(models.Question).filter(
        models.Question.test_id == test_id
    ).order_by(models.Question.question_number).all()
    
    return questions

# Отправить результаты теста
@app.post("/tests/{test_id}/submit", response_model=schemas.TestResultResponse)
def submit_test_results(
    test_id: int,
    test_data: schemas.TestSubmission,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправить результаты теста"""
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can submit tests"
        )
    
    # Проверяем существование теста
    test = db.query(models.Test).filter(models.Test.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    # Блокируем повторное прохождение теста
    existing = (
        db.query(models.TestResult)
        .join(models.UserAnswer, models.UserAnswer.test_result_id == models.TestResult.id)
        .join(models.Question, models.UserAnswer.question_id == models.Question.id)
        .filter(
            models.TestResult.user_id == current_user.id,
            models.Question.test_id == test_id
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test already completed"
        )
    
    testing_service = TestingService(db)
    
    # Рассчитываем общее время
    total_time = sum(answer.time_spent for answer in test_data.answers)
    
    # Сохраняем результаты
    test_result = testing_service.save_test_result(
        user_id=current_user.id,
        test_part=test_data.test_part,
        answers=test_data.answers,
        test_id=test_id,
        time_spent=total_time
    )
    
    return test_result

# Получить результаты всех тестов пользователя
@app.get("/tests/my-results", response_model=List[schemas.TestResultResponse])
def get_my_test_results(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все результаты тестов пользователя"""
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users can view test results"
        )
    
    results = db.query(models.TestResult).filter(
        models.TestResult.user_id == current_user.id
    ).order_by(models.TestResult.completed_at.desc()).all()
    
    return results

# Для психолога: получить детальные результаты теста пациента
@app.get("/psychologist/patient/{patient_id}/test/{test_result_id}/details")
def get_patient_test_details(
    patient_id: int,
    test_result_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Психолог получает детальные результаты теста пациента"""
    if current_user.role != "psychologist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can view patient test details"
        )
    
    # Проверяем, что пациент привязан к психологу
    patient = db.query(models.User).filter(
        models.User.id == patient_id,
        models.User.psychologist_id == current_user.id,
        models.User.role == "user"
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not linked to you"
        )
    
    # Проверяем, что пройдены все активные тесты
    total_tests = db.query(models.Test).filter(models.Test.is_active == True).count()
    completed_test_ids = set(
        t[0] for t in db.query(models.Question.test_id)
        .join(models.UserAnswer, models.UserAnswer.question_id == models.Question.id)
        .join(models.TestResult, models.TestResult.id == models.UserAnswer.test_result_id)
        .filter(models.TestResult.user_id == patient_id)
        .distinct()
        .all()
    )

    if total_tests == 0 or len(completed_test_ids) < total_tests:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient has not completed all tests"
        )

    # Получаем результат теста
    test_result = db.query(models.TestResult).filter(
        models.TestResult.id == test_result_id,
        models.TestResult.user_id == patient_id
    ).first()
    
    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found"
        )
    
    # Получаем детальные ответы
    user_answers = db.query(models.UserAnswer).filter(
        models.UserAnswer.test_result_id == test_result_id
    ).all()

    # Подсчёт правильных и условный процентиль по тесту (по проценту правильных)
    correct_count = sum(1 for ua in user_answers if ua.is_correct)
    total_count = len(user_answers)
    test_percentile = round((correct_count / total_count) * 100) if total_count else 0
    
    # Получаем вопросы
    questions_data = []
    for ua in user_answers:
        question = db.query(models.Question).filter(
            models.Question.id == ua.question_id
        ).first()
        
        if question:
            questions_data.append({
                "question_id": question.id,
                "question_number": question.question_number,
                "correct_answer": question.correct_answer,
                "user_answer": ua.user_answer,
                "is_correct": ua.is_correct,
                "time_spent": ua.time_spent
            })
    
    return {
        "test_result": test_result,
        "detailed_answers": questions_data,
        "correct_count": correct_count,
        "test_percentile": test_percentile
    }

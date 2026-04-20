from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# ============ USER SCHEMAS ============
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None  # Сделать необязательным
    role: str = "user"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    role: str = "user"

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    psychologist_id: Optional[int] = None
    
    @validator('date_of_birth', pre=True)
    def parse_date_of_birth(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value
    
    class Config:
        from_attributes = True

# ============ AUTH SCHEMAS ============
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# ============ TESTING SCHEMAS ============
class QuestionResponse(BaseModel):
    id: int
    question_number: int
    image_path: str
    test_id: int
    
    class Config:
        from_attributes = True

class TestInfo(BaseModel):
    id: int
    test_part: str
    test_number: int
    name: str
    description_image: str
    instruction_text: str
    time_limit: int
    question_count: int
    completed: Optional[bool] = False
    
    class Config:
        from_attributes = True

class TestAnswer(BaseModel):
    question_id: int
    answer: str  # 'a', 'b', 'c', 'd', 'e' или 'skip'
    time_spent: float  # время в секундах

class TestSubmission(BaseModel):
    test_part: str  # 'A' или 'B'
    answers: List[TestAnswer]

class TestResultBase(BaseModel):
    test_part: str
    raw_score_a: Optional[int] = None
    raw_score_b: Optional[int] = None
    total_raw_score: Optional[int] = None
    age_at_test: int
    age_group: str
    standard_score: Optional[float] = None
    percentile: Optional[int] = None
    interpretation: Optional[str] = None

class TestResultCreate(TestResultBase):
    user_id: int
    answers: Dict[str, Any]

class TestResultResponse(TestResultBase):
    id: int
    user_id: int
    completed_at: datetime
    
    class Config:
        from_attributes = True

# ============ PSYCHOLOGIST SCHEMAS ============
class PsychologistLink(BaseModel):
    psychologist_code: Optional[str] = None
    psychologist_email: Optional[str] = None

class UserWithTests(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    test_count: int
    last_test_date: Optional[datetime]
    
    class Config:
        from_attributes = True

# ============ UTILITY FUNCTIONS ============
def calculate_age(birth_date: date) -> int:
    """Рассчитать возраст по дате рождения"""
    if not birth_date:
        return 25  # Значение по умолчанию
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def get_age_group(age: int) -> str:
    """Определить возрастную группу"""
    if age < 18: return "16-17"
    elif age < 25: return "18-24"
    elif age < 35: return "25-34"
    elif age < 45: return "35-44"
    elif age < 55: return "45-54"
    elif age < 65: return "55-64"
    else: return "65+"

class TestResultResponse(BaseModel):
    id: int
    user_id: int
    test_part: str
    raw_score_a: Optional[int] = None
    raw_score_b: Optional[int] = None
    total_raw_score: Optional[int] = None
    age_at_test: int
    age_group: str
    standard_score: Optional[float] = None
    percentile: Optional[int] = None
    interpretation: Optional[str] = None
    completed_at: datetime
    time_spent: Optional[int] = None
    answers: Optional[Any] = None  # JSON со всеми ответами пользователя (может быть списком или словарем)
    
    class Config:
        from_attributes = True

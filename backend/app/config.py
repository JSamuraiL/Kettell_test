import os
from typing import Optional

class Settings:
    def __init__(self):
        # Docker PostgreSQL конфигурация
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://cattell_user:cattell_password@localhost:5432/cattell_db"
        )
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()

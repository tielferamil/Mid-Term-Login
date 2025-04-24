from beanie import Document
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class User(Document):
    email: EmailStr
    hashed_password: str
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"


class FoodItem(Document):
    user_id: str
    name: str
    calories: int
    timestamp: datetime = datetime.utcnow()

    class Settings:
        name = "foods"

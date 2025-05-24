from pydantic import BaseModel, EmailStr, Field


class Login(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str = Field(..., min_length=8)
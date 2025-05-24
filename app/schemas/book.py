from typing import Optional
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Базовая схема книги"""
    title: str
    author: str
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    quantity: int = Field(default=1, ge=0)
    description: Optional[str] = None


class BookCreate(BookBase):
    """Схема для создания книги"""
    pass


class BookUpdate(BaseModel):
    """Схема для обновления книги"""
    title: Optional[str] = None
    author: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None


class BookInDBBase(BookBase):
    """Базовая схема для книги в БД"""
    id: int

    class Config:
        orm_mode = True


class Book(BookInDBBase):
    """Схема для возвращаемой книги"""
    pass 
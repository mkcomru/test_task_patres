from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_book
from app.database.base import get_db
from app.models.user import User
from app.schemas.book import Book, BookCreate, BookUpdate
from app.security.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[Book])
def read_books(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    books = crud_book.get_books(db, skip=skip, limit=limit)
    return books


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if book_in.isbn:
        db_book = crud_book.get_book_by_isbn(db, isbn=book_in.isbn)
        if db_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга с таким ISBN уже существует",
            )
    book = crud_book.create_book(db, book=book_in)
    return book


@router.get("/{book_id}", response_model=Book)
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    book = crud_book.get_book(db, book_id=book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена",
        )
    return book


@router.put("/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    book = crud_book.get_book(db, book_id=book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена",
        )
    
    if book_in.isbn and book_in.isbn != book.isbn:
        db_book = crud_book.get_book_by_isbn(db, isbn=book_in.isbn)
        if db_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга с таким ISBN уже существует",
            )
    
    book = crud_book.update_book(db, db_book=book, book_in=book_in)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    book = crud_book.get_book(db, book_id=book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена",
        )
    crud_book.delete_book(db, db_book=book)
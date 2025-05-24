from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_borrowed_book, crud_book, crud_reader
from app.database.base import get_db
from app.models.user import User
from app.schemas.borrowed_book import (
    BorrowBookCreate, BorrowedBook, ReturnBook, BorrowedBookWithDetails
)
from app.security.dependencies import get_current_active_user

router = APIRouter()


@router.post("/borrow", response_model=BorrowedBook, status_code=status.HTTP_201_CREATED)
def borrow_book(
    borrow_data: BorrowBookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    book = crud_book.get_book(db, book_id=borrow_data.book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена",
        )
    
    reader = crud_reader.get_reader(db, reader_id=borrow_data.reader_id)
    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден",
        )
    
    if book.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет доступных экземпляров книги",
        )
    
    active_books_count = crud_borrowed_book.count_active_borrowed_books_by_reader(
        db, reader_id=borrow_data.reader_id
    )
    if active_books_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Читатель уже взял максимальное количество книг (3)",
        )
    
    existing_borrow = crud_borrowed_book.get_borrowed_book_by_book_and_reader(
        db, book_id=borrow_data.book_id, reader_id=borrow_data.reader_id
    )
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Эта книга уже выдана этому читателю",
        )
    
    borrowed_book = crud_borrowed_book.borrow_book(db, borrow_data=borrow_data)
    return borrowed_book


@router.post("/return", response_model=BorrowedBook)
def return_book(
    return_data: ReturnBook,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    borrow = crud_borrowed_book.get_borrowed_book(db, borrow_id=return_data.borrow_id)
    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись о выдаче не найдена",
        )
    
    if borrow.return_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Книга уже возвращена",
        )
    
    returned_book = crud_borrowed_book.return_book(db, db_borrow=borrow)
    return returned_book


@router.get("/reader/{reader_id}", response_model=List[BorrowedBook])
def get_active_borrowed_books_by_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    reader = crud_reader.get_reader(db, reader_id=reader_id)
    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Читатель не найден",
        )
    
    borrowed_books = crud_borrowed_book.get_active_borrowed_books_by_reader(
        db, reader_id=reader_id
    )
    return borrowed_books


@router.get("/", response_model=List[BorrowedBook])
def get_all_borrowed_books(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    borrowed_books = crud_borrowed_book.get_all_borrowed_books(
        db, skip=skip, limit=limit
    )
    return borrowed_books
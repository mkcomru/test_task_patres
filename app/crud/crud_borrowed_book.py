from typing import List, Optional
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.borrowed_book import BorrowedBook
from app.models.book import Book
from app.schemas.borrowed_book import BorrowBookCreate


def get_borrowed_book(db: Session, borrow_id: int) -> Optional[BorrowedBook]:
    return db.query(BorrowedBook).filter(BorrowedBook.id == borrow_id).first()


def get_active_borrowed_books_by_reader(db: Session, reader_id: int) -> List[BorrowedBook]:
    return db.query(BorrowedBook).filter(
        and_(
            BorrowedBook.reader_id == reader_id,
            BorrowedBook.return_date.is_(None)
        )
    ).all()


def get_borrowed_book_by_book_and_reader(
    db: Session, book_id: int, reader_id: int
) -> Optional[BorrowedBook]:
    return db.query(BorrowedBook).filter(
        and_(
            BorrowedBook.book_id == book_id,
            BorrowedBook.reader_id == reader_id,
            BorrowedBook.return_date.is_(None)
        )
    ).first()


def count_active_borrowed_books_by_reader(db: Session, reader_id: int) -> int:
    return db.query(BorrowedBook).filter(
        and_(
            BorrowedBook.reader_id == reader_id,
            BorrowedBook.return_date.is_(None)
        )
    ).count()


def borrow_book(db: Session, borrow_data: BorrowBookCreate) -> BorrowedBook:
    db_book = db.query(Book).filter(Book.id == borrow_data.book_id).first()
    if db_book.quantity <= 0:
        raise ValueError("Нет доступных экземпляров книги")
    
    active_books_count = count_active_borrowed_books_by_reader(
        db, reader_id=borrow_data.reader_id
    )
    if active_books_count >= 3:
        raise ValueError("Читатель уже взял максимальное количество книг (3)")
    
    db_borrow = BorrowedBook(
        book_id=borrow_data.book_id,
        reader_id=borrow_data.reader_id,
        borrow_date=datetime.utcnow()
    )
    db.add(db_borrow)
    
    db_book.quantity -= 1
    db.add(db_book)
    
    db.commit()
    db.refresh(db_borrow)
    return db_borrow


def return_book(db: Session, db_borrow: BorrowedBook) -> BorrowedBook:
    if db_borrow.return_date:
        raise ValueError("Книга уже возвращена")
    
    db_borrow.return_date = datetime.utcnow()
    db.add(db_borrow)
    
    db_book = db.query(Book).filter(Book.id == db_borrow.book_id).first()
    db_book.quantity += 1
    db.add(db_book)
    
    db.commit()
    db.refresh(db_borrow)
    return db_borrow


def get_all_borrowed_books(db: Session, skip: int = 0, limit: int = 100) -> List[BorrowedBook]:
    return db.query(BorrowedBook).offset(skip).limit(limit).all()
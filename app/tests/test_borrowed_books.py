import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.crud import crud_book, crud_reader, crud_borrowed_book
from app.schemas.book import BookCreate
from app.schemas.reader import ReaderCreate
from app.schemas.borrowed_book import BorrowBookCreate


def test_borrow_book_success(db: Session):
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        publication_year=2020,
        isbn="1234567890",
        quantity=1
    )
    book = crud_book.create_book(db, book=book_data)
    
    reader_data = ReaderCreate(
        name="Test Reader",
        email="reader@example.com"
    )
    reader = crud_reader.create_reader(db, reader=reader_data)
    
    borrow_data = BorrowBookCreate(book_id=book.id, reader_id=reader.id)
    borrowed_book = crud_borrowed_book.borrow_book(db, borrow_data=borrow_data)
    
    assert borrowed_book.book_id == book.id
    assert borrowed_book.reader_id == reader.id
    assert borrowed_book.return_date is None
    
    updated_book = crud_book.get_book(db, book_id=book.id)
    assert updated_book.quantity == 0


def test_borrow_book_no_available_copies(db: Session):
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        publication_year=2020,
        isbn="1234567890",
        quantity=0
    )
    book = crud_book.create_book(db, book=book_data)
    
    reader_data = ReaderCreate(
        name="Test Reader",
        email="reader@example.com"
    )
    reader = crud_reader.create_reader(db, reader=reader_data)
    
    with pytest.raises(ValueError):
        borrow_data = BorrowBookCreate(book_id=book.id, reader_id=reader.id)
        crud_borrowed_book.borrow_book(db, borrow_data=borrow_data)


def test_borrow_book_max_limit(db: Session):
    reader_data = ReaderCreate(
        name="Test Reader",
        email="reader@example.com"
    )
    reader = crud_reader.create_reader(db, reader=reader_data)
    
    books = []
    for i in range(4):
        book_data = BookCreate(
            title=f"Test Book {i}",
            author="Test Author",
            publication_year=2020,
            isbn=f"123456789{i}",
            quantity=1
        )
        books.append(crud_book.create_book(db, book=book_data))
    
    for i in range(3):
        borrow_data = BorrowBookCreate(book_id=books[i].id, reader_id=reader.id)
        crud_borrowed_book.borrow_book(db, borrow_data=borrow_data)
    
    active_books = crud_borrowed_book.get_active_borrowed_books_by_reader(db, reader_id=reader.id)
    assert len(active_books) == 3
    
    with pytest.raises(ValueError):
        borrow_data = BorrowBookCreate(book_id=books[3].id, reader_id=reader.id)
        crud_borrowed_book.borrow_book(db, borrow_data=borrow_data)


def test_return_book_success(db: Session):
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        publication_year=2020,
        isbn="1234567890",
        quantity=1
    )
    book = crud_book.create_book(db, book=book_data)
    
    reader_data = ReaderCreate(
        name="Test Reader",
        email="reader@example.com"
    )
    reader = crud_reader.create_reader(db, reader=reader_data)
    
    borrow_data = BorrowBookCreate(book_id=book.id, reader_id=reader.id)
    borrowed_book = crud_borrowed_book.borrow_book(db, borrow_data=borrow_data)
    
    updated_book = crud_book.get_book(db, book_id=book.id)
    assert updated_book.quantity == 0
    
    returned_book = crud_borrowed_book.return_book(db, db_borrow=borrowed_book)
    
    assert returned_book.return_date is not None
    
    updated_book = crud_book.get_book(db, book_id=book.id)
    assert updated_book.quantity == 1


def test_return_already_returned_book(db: Session):
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        publication_year=2020,
        isbn="1234567890",
        quantity=1
    )
    book = crud_book.create_book(db, book=book_data)
    
    reader_data = ReaderCreate(
        name="Test Reader",
        email="reader@example.com"
    )
    reader = crud_reader.create_reader(db, reader=reader_data)
    
    borrow_data = BorrowBookCreate(book_id=book.id, reader_id=reader.id)
    borrowed_book = crud_borrowed_book.borrow_book(db, borrow_data=borrow_data)
    
    returned_book = crud_borrowed_book.return_book(db, db_borrow=borrowed_book)
    
    with pytest.raises(ValueError):
        crud_borrowed_book.return_book(db, db_borrow=returned_book)
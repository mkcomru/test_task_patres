import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.book import BookCreate
from app.schemas.reader import ReaderCreate
from app.schemas.borrowed_book import BorrowBookCreate
from app.crud.crud_book import create_book
from app.crud.crud_reader import create_reader
from app.crud.crud_borrowed_book import borrow_book


def test_borrow_book_api(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_borrow@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_borrow@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    book_data = BookCreate(
        title="Book to Borrow",
        author="Author",
        publication_year=2020,
        isbn="1234567890",
        quantity=1
    )
    book = create_book(db, book=book_data)
    
    reader_data = ReaderCreate(
        name="Reader",
        email="reader_borrow@example.com"
    )
    reader = create_reader(db, reader=reader_data)
    
    borrow_data = {
        "book_id": book.id,
        "reader_id": reader.id
    }
    
    response = client.post("/api/v1/borrowed-books/borrow", headers=headers, json=borrow_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["book_id"] == book.id
    assert data["reader_id"] == reader.id
    assert data["return_date"] is None
    
    response = client.post("/api/v1/borrowed-books/borrow", headers=headers, json=borrow_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    book2_data = BookCreate(
        title="Book with Zero Quantity",
        author="Author",
        publication_year=2020,
        isbn="0987654321",
        quantity=0
    )
    book2 = create_book(db, book=book2_data)
    
    borrow_data = {
        "book_id": book2.id,
        "reader_id": reader.id
    }
    
    response = client.post("/api/v1/borrowed-books/borrow", headers=headers, json=borrow_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_return_book_api(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_return@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_return@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    book_data = BookCreate(
        title="Book to Return",
        author="Author",
        publication_year=2020,
        isbn="5566778899",
        quantity=1
    )
    book = create_book(db, book=book_data)
    
    reader_data = ReaderCreate(
        name="Reader",
        email="reader_return@example.com"
    )
    reader = create_reader(db, reader=reader_data)
    
    borrow_data = BorrowBookCreate(
        book_id=book.id,
        reader_id=reader.id
    )
    borrowed_book = borrow_book(db, borrow_data=borrow_data)
    
    return_data = {
        "borrow_id": borrowed_book.id
    }
    
    response = client.post("/api/v1/borrowed-books/return", headers=headers, json=return_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["book_id"] == book.id
    assert data["reader_id"] == reader.id
    assert data["return_date"] is not None
    
    response = client.post("/api/v1/borrowed-books/return", headers=headers, json=return_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    return_data = {
        "borrow_id": 999
    }
    
    response = client.post("/api/v1/borrowed-books/return", headers=headers, json=return_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_active_borrowed_books_by_reader(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_get_books@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_get_books@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    reader_data = ReaderCreate(
        name="Reader",
        email="reader_get@example.com"
    )
    reader = create_reader(db, reader=reader_data)
    
    books = []
    for i in range(2):
        book_data = BookCreate(
            title=f"Book {i}",
            author="Author",
            publication_year=2020,
            isbn=f"123456789{i}",
            quantity=1
        )
        books.append(create_book(db, book=book_data))
    
    for book in books:
        borrow_data = BorrowBookCreate(
            book_id=book.id,
            reader_id=reader.id
        )
        borrow_book(db, borrow_data=borrow_data)
    
    response = client.get(f"/api/v1/borrowed-books/reader/{reader.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    
    response = client.get("/api/v1/borrowed-books/reader/999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_borrowed_books(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_all_books@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_all_books@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    reader_data = ReaderCreate(
        name="Reader",
        email="reader_all@example.com"
    )
    reader = create_reader(db, reader=reader_data)
    
    book_data = BookCreate(
        title="Book for All Test",
        author="Author",
        publication_year=2020,
        isbn="1122334455",
        quantity=1
    )
    book = create_book(db, book=book_data)
    
    borrow_data = BorrowBookCreate(
        book_id=book.id,
        reader_id=reader.id
    )
    borrow_book(db, borrow_data=borrow_data)
    
    response = client.get("/api/v1/borrowed-books/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1 
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.book import BookCreate, BookUpdate
from app.crud.crud_book import create_book


def test_create_book(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_books@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_books@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "publication_year": 2020,
        "isbn": "1234567890",
        "quantity": 5
    }
    
    response = client.post("/api/v1/books/", headers=headers, json=book_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["publication_year"] == 2020
    assert data["isbn"] == "1234567890"
    assert data["quantity"] == 5
    
    response = client.post("/api/v1/books/", headers=headers, json=book_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_read_books(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_read_books@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_read_books@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(3):
        book_data = BookCreate(
            title=f"Test Book {i}",
            author=f"Test Author {i}",
            publication_year=2020 + i,
            isbn=f"123456789{i}",
            quantity=i + 1
        )
        create_book(db, book=book_data)
    
    response = client.get("/api/v1/books/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3
    
    response = client.get("/api/v1/books/1", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    response = client.get("/api/v1/books/999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_book(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_update_book@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_update_book@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    book_data = BookCreate(
        title="Original Title",
        author="Original Author",
        publication_year=2020,
        isbn="0987654321",
        quantity=3
    )
    book = create_book(db, book=book_data)
    
    update_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "quantity": 5
    }
    
    response = client.put(f"/api/v1/books/{book.id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Updated Author"
    assert data["quantity"] == 5
    assert data["isbn"] == "0987654321" 
    
    another_book_data = BookCreate(
        title="Another Book",
        author="Another Author",
        publication_year=2021,
        isbn="1122334455",
        quantity=1
    )
    another_book = create_book(db, book=another_book_data)
    
    update_data = {"isbn": "1122334455"}
    response = client.put(f"/api/v1/books/{book.id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    response = client.put("/api/v1/books/999", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_book(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_delete_book@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_delete_book@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    book_data = BookCreate(
        title="Book to Delete",
        author="Author",
        publication_year=2020,
        isbn="5566778899",
        quantity=1
    )
    book = create_book(db, book=book_data)
    
    response = client.delete(f"/api/v1/books/{book.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    response = client.get(f"/api/v1/books/{book.id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response = client.delete("/api/v1/books/999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND 
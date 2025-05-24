import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.reader import ReaderCreate, ReaderUpdate
from app.crud.crud_reader import create_reader


def test_create_reader(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_readers@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_readers@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    reader_data = {
        "name": "Test Reader",
        "email": "reader@example.com"
    }
    
    response = client.post("/api/v1/readers/", headers=headers, json=reader_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Reader"
    assert data["email"] == "reader@example.com"
    
    response = client.post("/api/v1/readers/", headers=headers, json=reader_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_read_readers(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_read_readers@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_read_readers@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(3):
        reader_data = ReaderCreate(
            name=f"Reader {i}",
            email=f"reader{i}@example.com"
        )
        create_reader(db, reader=reader_data)
    
    response = client.get("/api/v1/readers/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3
    
    response = client.get("/api/v1/readers/1", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    response = client.get("/api/v1/readers/999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_reader(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_update_reader@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_update_reader@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    reader_data = ReaderCreate(
        name="Original Name",
        email="original@example.com"
    )
    reader = create_reader(db, reader=reader_data)
    
    update_data = {
        "name": "Updated Name"
    }
    
    response = client.put(f"/api/v1/readers/{reader.id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "original@example.com" 
    
    another_reader_data = ReaderCreate(
        name="Another Reader",
        email="another@example.com"
    )
    another_reader = create_reader(db, reader=another_reader_data)
    
    update_data = {"email": "another@example.com"}
    response = client.put(f"/api/v1/readers/{reader.id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    response = client.put("/api/v1/readers/999", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_reader(client, db):
    from app.schemas.user import UserCreate
    from app.crud.crud_user import create_user
    
    user_data = UserCreate(email="test_delete_reader@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test_delete_reader@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    reader_data = ReaderCreate(
        name="Reader to Delete",
        email="to_delete@example.com"
    )
    reader = create_reader(db, reader=reader_data)
    
    response = client.delete(f"/api/v1/readers/{reader.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    response = client.get(f"/api/v1/readers/{reader.id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response = client.delete("/api/v1/readers/999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND 
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.user import UserCreate
from app.crud.crud_user import create_user

client = TestClient(app)

def test_register_user(client, db):
    user_data = {
        "email": "new_user@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "new_user@example.com"
    assert "id" in data
    assert "hashed_password" not in data
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_user(client, db):
    user_data = UserCreate(email="login_test@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {
        "email": "login_test@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    login_data = {
        "email": "login_test@example.com",
        "password": "wrong_password"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_with_token(client, db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    login_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/books/", headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_protected_endpoint_without_token():
    response = client.get("/api/v1/books/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_oauth_login(client, db):
    user_data = UserCreate(email="oauth_test@example.com", password="password123")
    user = create_user(db, user_in=user_data)
    
    response = client.post(
        "/api/v1/auth/login/oauth",
        data={"username": "oauth_test@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    response = client.post(
        "/api/v1/auth/login/oauth",
        data={"username": "oauth_test@example.com", "password": "wrong_password"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
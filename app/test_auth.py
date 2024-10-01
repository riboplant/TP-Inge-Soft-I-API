import sys
import os
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connect import get_db
from app.main import app
from app.database.models import Base, Users
from app.services.auth import get_password_hash

# Configuración de la base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

# Override para usar la base de datos de prueba
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Anular la dependencia de la base de datos en la aplicación
app.dependency_overrides[get_db] = override_get_db

# Cliente para hacer peticiones a la API
client = TestClient(app)

# Fixture para crear un usuario de prueba
@pytest.fixture(scope="module")
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpassword",
        "name": "Test User",
        "address": "Test Address",
        "dni": "12345678"
    }

# Fixture para registrar un usuario de prueba
@pytest.fixture(scope="module")
def test_register_user(test_user):
    response = client.post("/auth/users/register", json=test_user)
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}

# Test para evitar el registro de usuarios duplicados
def test_register_duplicate_user(test_user):
    response = client.post("/auth/users/register", json=test_user)
    assert response.status_code == 422

# Test para obtener un token de acceso al iniciar sesión
def test_login_for_access_token(test_user):
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Test para evitar el inicio de sesión con una contraseña incorrecta
def test_login_with_incorrect_password(test_user):
    response = client.post("/auth/token", data={
        "username": test_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401

# Test para leer los datos del usuario autenticado
def test_read_users_me(test_user):
    # Primero, obtenemos un token
    login_response = client.post("/auth/token", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    
    # Luego, usamos el token para acceder a /users/me/
    response = client.get("/auth/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]

# Test para evitar acceder a /users/me/ sin un token
def test_read_users_me_without_token():
    response = client.get("/auth/users/me/")
    assert response.status_code == 401

# Fixture para crear un usuario inactivo
@pytest.fixture(scope="module")
def inactive_user():
    return {
        "email": "inactive@example.com",
        "password": "inactivepassword",
        "name": "Inactive User",
        "address": "Inactive Address",
        "dni": "87654321",
        "disabled": True
    }

# Test para evitar que un usuario inactivo inicie sesión
def test_inactive_user(inactive_user):
    # Registrar usuario inactivo
    db_user = Users(
        user_id=str(uuid4()),
        email=inactive_user["email"],
        hashed_password=get_password_hash(inactive_user["password"]),
        name=inactive_user["name"],
        address=inactive_user["address"],
        dni=inactive_user["dni"],
        disabled=True
    )
    
    db = TestingSessionLocal()
    db.add(db_user)
    db.commit()

    # Intentar iniciar sesión con usuario inactivo
    response = client.post("/auth/token", data={
        "username": inactive_user["email"],
        "password": inactive_user["password"]
    })
    assert response.status_code == 400
    assert "Inactive user" in response.json()["detail"]

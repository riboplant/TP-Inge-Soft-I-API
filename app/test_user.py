import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connect import get_db, SessionLocal
from app.main import app
from app.database.models import Base, Users, Drivers, Vehicles, Drives
from app.services.auth import get_password_hash, create_access_token
from uuid import uuid4

# Configuración de la base de datos de pruebas en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# Cliente para hacer peticiones a la API
client = TestClient(app)

from sqlalchemy import inspect

@pytest.fixture(scope="module")
def test_db():
    # Crea todas las tablas en la base de datos de pruebas
    Base.metadata.create_all(bind=engine)

    # Verificar si las tablas están creadas
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tablas creadas: {tables}")

    # Reemplaza la función get_db con la sesión de prueba
    app.dependency_overrides[get_db] = lambda: TestingSessionLocal()

    yield

    # Limpia la base de datos después de las pruebas
    Base.metadata.drop_all(bind=engine)



@pytest.fixture(scope="module", autouse=True)
def test_setup(test_db):
    pass
# Cliente para hacer peticiones a la API
client = TestClient(app)
temp_id = ""

@pytest.fixture(scope="module")
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpassword",
        "name": "Test User",
        "address": "Test Address",
        "dni": "12345678"
    }

@pytest.fixture(scope="module")
def test_register_user(test_user):
    response = client.post("/auth/users/register", json=test_user)
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}
    db = get_db()
    assert db.query(Users).filter_by(email=test_user["email"]).first() is not None


@pytest.fixture(scope="module")
def test_create_user(test_user):
    global temp_id  # Hacer que temp_id sea global
    db = TestingSessionLocal()
    try:
        db_user = Users(
            user_id=str(uuid4()),
            email=test_user["email"],
            hashed_password=get_password_hash("testpassword"),
            name=test_user["name"],
            address=test_user["address"],
            dni=test_user["dni"],
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print("Hashed Password: " + db_user.hashed_password)
        print(get_password_hash("testpassword"))
        temp_id = db_user.user_id  # Guardar el ID del usuario creado

        # Verificación explícita
        created_user = db.query(Users).filter_by(email=test_user["email"]).first()
        print(f"Usuario creado: {created_user}")  # Verificar si el usuario se creó correctamente

        assert created_user is not None  # Si esto falla, el usuario no se ha creado
        assert created_user.email == test_user["email"]
        return created_user  # Retornar el usuario creado para las siguientes pruebas

    finally:
        db.close()


def test_database_synchronization(test_create_user):
    db = TestingSessionLocal()
    user = db.query(Users).filter_by(email="test@example.com").first()
    print(f"Usuario en la base de datos: {user.email}, Hash: {user.hashed_password}")
    
    assert user is not None




@pytest.fixture(scope="module")
def test_token(test_create_user):
    user = test_create_user
    print(f"Usuario creado: {user.email}, hash: {user.hashed_password}")  # Log para verificar datos

    response = client.post("/auth/token", data={
        "grant_type": "",
        "username": "test@example.com",
        "password": "testpassword"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})

    print("In token: " + get_password_hash("testpassword"))
    print(f"Respuesta del servidor: {response.json()}")  # Para ver la respuesta del servidor

    assert response.status_code == 200
    assert "access_token" in response.json()
    a_t = response.json()["access_token"]  # Obtener el token del JSON
    return a_t




def test_edit_user_photo_bad_url(test_token):
    base64_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q=="
    response = client.put("/users/edit/photo", headers={"Authorization": f"Bearer {test_token}"}, json={"base_64_image": base64_image})
    assert response.status_code == 500

def test_delete_user_photo(test_token):
    response = client.delete("/users/delete/photo", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200 
    assert response.json()["message"] == "Image deleted successfully"

def test_make_user_driver(test_token):
    response = client.post("/users/driver", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200

def test_add_user_car(test_token):
    vehicle_data = {
        "color": "red",
        "model": "Toyota Corolla",
        "plate": "ABC123"
    }
    response = client.post("/users/addcar", headers={"Authorization": f"Bearer {test_token}"}, json=vehicle_data)
    assert response.status_code == 200

def test_get_user_cars_with_car(test_token):
    response = client.get("/users/mycars", headers={"Authorization": f"Bearer {test_token}"})
    
    assert response.status_code == 200

    vehicles = response.json()
    assert len(vehicles) > 0  
    
    assert "Usuario" in vehicles[0]  
    assert vehicles[0]["Usuario"] == "Usuario con id = {user_id} no exits"  


def test_remove_user_car(test_token):
    response = client.delete("/users/removecar?plate=ABC123", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200

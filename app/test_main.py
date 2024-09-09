from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_register_user():
    response = client.post(
        "/auth/users/register",
        json = { "name": "test", "rider_rating": 5, "email": "string", "password": "test password", 
                "disabled": True, "address": "string", "dni": 0, "status": "string", "photo_id": 0 } )
    assert response.status_code == 200
    assert response.json() == { "msg": "User registered successfully" }


def test_login_user():
    response = client.post("/auth/token", "", "test", "test password", "", "", "")
    assert response.status_code == 200
    token = response.json().access_token
    assert response.json() == { "access_token": token, "token_type": "bearer" }
    return token

def test_get_user_info():
    token = test_login_user()
    response = client.get("/users/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    id = response.json().user_id
    assert response.json() == { "rider_rating": None, "hashed_password": "$2b$12$4fdxxKNPixLNbPvMsztT/.cS9H9lnYPxZ9z9o1xetC620cpaOeZZ2",
                                "name": "test", "address": None, "status": None, "email": "string", "user_id": id,
                                "disabled": False, "dni": None, "photo_id": None }
    
def test_get_other_user_info():
    token = test_login_user()
    response = client.get("/users/d7f79f1e-afaa-468d-91f6-610b44d4c536", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == { "rider_rating": None, "hashed_password": "$2b$12$mphhSBeows2.qB2PLnQkG.eDXOQBb5xkYI28qxmsMi00RmuqBPWdy",
                                "name": "Ini", "address": "string", "status": None, "email": "string", "user_id": "d7f79f1e-afaa-468d-91f6-610b44d4c536",
                                "disabled": False, "dni": None, "photo_id": 0 }
    
def test_users_edit():
    token = test_login_user()
    response = client.put("/users/edit", headers={"Authorization": f"Bearer {token}"}, json = {{
  "name": "test", "rider_rating": 5, "email": "testemail", "disabled": True, "address": "testaddress",
  "dni": 2, "status": "string", "photo_id": 0 }})
    assert response.status_code == 200
    id = response.json().user_id
    assert response.json() == { "name": "test", "rider_rating": None, "email": "string", "disabled": False,
                                "address": None, "dni": None, "status": None, "photo_id": None, "hashed_password": "$2b$12$4fdxxKNPixLNbPvMsztT/.cS9H9lnYPxZ9z9o1xetC620cpaOeZZ2",
                                "user_id": "c3e65bb2-96d9-4540-9b89-eb7c4a9f36f4" }
    


    # Para este hay q primero crear lo de agregar un auto xq pide plate
# def test_create_ride_detail():
#     token = test_login_user()
#     response = client.post("/users/users/me", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200

#Luego falta agregar, borrar auto, borrar ride, borrar user
#Tambien chequear que den los errores donde corresponde
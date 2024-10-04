from typing import List
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from schemas.users_schemas import *
from database.models import *
from database.connect import get_db
from services.auth import get_current_active_user
from uuid import uuid4
from services.users import *



router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_user_data(current_user, db)

@router.put("/edit/photo")
async def edit_user_photo(base64Image: Base_64, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await edit_photo(base64Image.base_64_image, current_user, db)
    

@router.delete("/delete/photo")
async def delete_user_photo(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return delete_photo(current_user, db)

@router.put("/edit/name")
async def edit_user_name(name: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return edit_name(name, current_user, db)


@router.get("/mycars")
async def get_user_cars(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_cars(current_user, db)
    

@router.post("/addcar")
async def add_user_car(vehicle: Vehicle, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return add_car(vehicle, current_user, db)
        

@router.delete("/removecar")
async def remove_user_car(plate: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return remove_car(plate, current_user, db)


@router.post("/driver")
async def make_user_driver(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return make_driver(current_user, db)



# @router.get("/{user_id}")
# async def get_user_from_id(user_id : str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
#     response = db.query(Users).filter(Users.user_id == user_id).first()
#     if response is None:
#         return [{"Usuario": "Usuario con id = {user_id} no exits"}]
    
#     return response
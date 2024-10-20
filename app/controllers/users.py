from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from schemas.users_schemas import Base_64, User, Vehicle
from database.connect import get_db
from services.auth import get_current_active_user
from services import users


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return users.get_user_data(current_user, db)

@router.put("/edit/photo")
async def edit_user_photo(base64Image: Base_64, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await users.edit_photo(base64Image.base_64_image, current_user, db)
    

@router.delete("/delete/photo")
async def delete_user_photo(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return users.delete_photo(current_user, db)

@router.put("/edit/name")
async def edit_user_name(name: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return users.edit_name(name, current_user, db)


@router.get("/mycars")
async def get_user_cars(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return users.get_cars(current_user, db)
    

@router.post("/addcar")
async def add_user_car(vehicle: Vehicle, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return users.add_car(vehicle, current_user, db)
        

@router.delete("/removecar")
async def remove_user_car(plate: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return users.remove_car(plate, current_user, db)


@router.post("/driver")
async def make_user_driver(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return users.make_driver(current_user, db)

@router.get("/profile/driver/{driver_id}")
async def get_driver_comments(driver_id: str, db: Session = Depends(get_db)):
    return users.get_driver_profile(driver_id, db)

@router.get("/profile/rider/{user_id}")
async def get_rider_comments(user_id: str, db: Session = Depends(get_db)):
    return users.get_rider_profile(user_id, db)
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
    return db.query(Users).filter(Users.user_id == current_user.user_id).first()

@router.get("/{user_id}") #esto me permite ver el perfil de otro usuario con datos y resenas correspondientes, debo estar loguado
async def get_user_from_id(user_id : str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    response = db.query(Users).filter(Users.user_id == user_id).first()
    if response is None:
        return [{"Usuario": "Usuario con id = {user_id} no exits"}]
    
    return response
    
@router.put("/edit/photo")#tenes que estar logueado permite editar el perfil del current
async def edit_user_photo(base64Image: Base_64, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    ans = await edit_photo(base64Image.base_64_image, current_user, db)
    return ans


@router.put("/edit/name")#tenes que estar logueado permite editar el perfil del current
async def edit_user_name(name: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return 0


@router.get("/mycars")
async def get_user_cars(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    #Checking if user is driver
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=402, detail="User is not a driver")
    
    vehicles = db.query(Vehicles).join(Drives).filter(Drives.driver_id == driver.driver_id).all()
    
    vehicle_list = [{"plate": vehicle.plate, "model": vehicle.model} for vehicle in vehicles]

    if not vehicles:
        raise HTTPException(status_code=403, detail="No vehicles found")
    
    return vehicle_list


@router.post("/addcar")
async def add_user_car(vehicle: Vehicle, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    #Checking if user is a driver
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=403, detail="User is not a driver")

    id = driver.driver_id
    car = db.query(Vehicles).filter(Vehicles.plate == vehicle.plate).first()

    if not car:
        vehicle_model = Vehicles()
        vehicle_model.color = vehicle.color
        vehicle_model.model = vehicle.model
        vehicle_model.status = "Unchecked"
        vehicle_model.plate = vehicle.plate
        db.add(vehicle_model)


    db.commit()
    drive_model = Drives()
    drive_model.plate = vehicle.plate
    drive_model.driver_id = id
    db.add(drive_model)
    db.commit()
        

@router.delete("/removecar")
async def remove_user_car(plate: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    #Checking if user is a driver
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        return {"User is not a driver"}

    id = driver.driver_id
    car = db.query(Drives).filter(Drives.plate == plate, Drives.driver_id == id).delete()
    db.commit()

    return car                     

@router.post("/driver")
async def make_user_driver(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    driver_model = Drivers()

    driver_model.user_id = current_user.user_id
    driver_model.driver_id = str(uuid4())
    driver_model.driving_license = 0
    driver_model.driver_rating = 0
    driver_model.status = 0

    db.add(driver_model)
    db.commit()
    return driver_model.driver_id
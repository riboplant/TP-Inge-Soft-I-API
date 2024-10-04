import os
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from schemas.users_schemas import *
from database.models import *
from database.connect import get_db
from services.auth import get_current_active_user
from uuid import uuid4
from utils.imgBBAPI import *
from fastapi.responses import JSONResponse


def get_user_data(current_user, db):
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()
    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    
    user = UserData(
        name=user_model.name,
        email=user_model.email,
        address=user_model.address,
        dni=user_model.dni,
        photo_url=user_model.photo_url
    )

    return user


async def edit_photo(base64Image: str, current_user, db):
    
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    
    try:
        img = await upload_image(base64Image)
        
    except:
        
        raise HTTPException(
            status_code=500,
            detail="Error uploading image"
        )
    try:
        setattr(user_model, "photo_url", img["photo_url"])
        setattr(user_model, "delete_photo_url", img["delete_photo_url"])

        db.commit()
        db.refresh(user_model)
        
        
    except:
        raise HTTPException(
            status_code=500,
            detail="Error updating image in db"
        )
   
    return {"photo_url":img["photo_url"]}



def delete_photo(current_user, db):
    try:
        user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()
        setattr(user_model, "photo_url", None)
        setattr(user_model, "delete_photo_url", None)
        db.commit()
        db.refresh(user_model)
    except:
        raise HTTPException(
            status_code=500,
            detail="Error deleting image"
        )
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Image deleted successfully"})


def get_cars(current_user, db):

    #Checking if user is driver
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=402, detail="User is not a driver")
    
    vehicles = db.query(Vehicles).join(Drives).filter(Drives.driver_id == driver.driver_id).all()
    
    vehicle_list = [{"plate": vehicle.plate, "model": vehicle.model} for vehicle in vehicles]
    
    return vehicle_list


def add_car(vehicle, current_user, db):
    
    
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
        try:
            db.add(vehicle_model)
            db.commit()
        except:
            raise HTTPException(status_code=500, detail="Error adding vehicle")

    drives = db.query(Drives).filter(Drives.plate == vehicle.plate, Drives.driver_id == id).first()
    if not drives:
        drive_model = Drives()
        drive_model.plate = vehicle.plate
        drive_model.driver_id = id
        try:
            db.add(drive_model)
            db.commit()
        except:
            raise HTTPException(status_code=500, detail="Error adding vehicle to driver")
    
    else:
        raise HTTPException(status_code=401, detail="Vehicle already added")
    
    return {"message": "Vehicle added successfully"}


def remove_car(plate: str, current_user, db):
    
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        return HTTPException(status_code=403, detail="User is not a driver")

    id = driver.driver_id

    drives = db.query(Drives).filter(Drives.plate == plate, Drives.driver_id == id).first()
    
    if not drives:
        return HTTPException(status_code=401, detail="Vehicle not found")
    try:
        db.delete(drives)
        db.commit()
    except:
        return HTTPException(status_code=500, detail="Error removing vehicle")

    aux = db.query(Drives).filter(Drives.plate == plate).first()

    if not aux:
        car = db.query(Vehicles).filter(Vehicles.plate == plate).first()
        try:
            db.delete(car)
            db.commit()
        except:
            return HTTPException(status_code=500, detail="Error removing vehicle")

    return 0

def make_driver(current_user, db):

    if(db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()):
        return HTTPException(status_code=403, detail="User is already a driver")
    
    driver_model = Drivers()

    driver_model.user_id = current_user.user_id
    driver_model.driver_id = str(uuid4())
    driver_model.driving_license = 0
    driver_model.driver_rating = 0
    driver_model.status = 0
    try:
        db.add(driver_model)
        db.commit()
    except:
        return HTTPException(status_code=500, detail="Error making user driver")
    
    return driver_model.driver_id

def edit_name(name: str, current_user, db):
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()
    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    if not name or len(name) < 1:
        raise HTTPException(status_code=400, detail="Nombre no puede estar vacío")
    try:
        setattr(user_model, "name", name)
        db.commit()
        db.refresh(user_model)
    except:
        raise HTTPException(
            status_code=500,
            detail="Error updating name in db"
        )
    return {"name": name}                 
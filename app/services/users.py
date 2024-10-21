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
        photo_url=user_model.photo_url,
        is_driver=False,
        user_id=user_model.user_id
    )

    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()

    if driver:
        user.is_driver = True
    

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
    
    plate = vehicle.plate.split(" ")[0]
    
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=403, detail="User is not a driver")

    id = driver.driver_id
    car = db.query(Vehicles).filter(Vehicles.plate == plate).first()

    if not car:
        vehicle_model = Vehicles()
        vehicle_model.color = vehicle.color
        vehicle_model.model = vehicle.model
        vehicle_model.status = "Unchecked"
        vehicle_model.plate = plate
        try:
            db.add(vehicle_model)
            db.commit()
        except:
            raise HTTPException(status_code=500, detail="Error adding vehicle")

    drives = db.query(Drives).filter(Drives.plate == plate, Drives.driver_id == id).first()
    if not drives:
        drive_model = Drives()
        drive_model.plate = plate
        drive_model.driver_id = id
        try:
            db.add(drive_model)
            db.commit()
        except:
            raise HTTPException(status_code=500, detail="Error adding vehicle to driver")
    
    else:
        raise HTTPException(status_code=402, detail="Vehicle already added")
    
    return {"message": "Vehicle added successfully"}


def remove_car(plate: str, current_user, db):
    
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=403, detail="User is not a driver")

    id = driver.driver_id

    drives = db.query(Drives).filter(Drives.plate == plate.split(" ")[0], Drives.driver_id == id).first()
    
    if not drives:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    try:
        db.delete(drives)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error removing vehicle")

    aux = db.query(Drives).filter(Drives.plate == plate).first()
    ride = db.query(Rides).filter(Rides.car_plate == plate).first()

    if not aux and not ride:
        car = db.query(Vehicles).filter(Vehicles.plate == plate).first()
        try:
            db.delete(car)
            db.commit()
        except:
            raise HTTPException(status_code=500, detail="Error removing vehicle")
    else: 
        return {"message": "Vehicle no longer available"}
    return {"message": "Vehicle removed successfully"}

def make_driver(current_user, db):

    if(db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()):
        raise HTTPException(status_code=403, detail="User is already a driver")
    
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
        raise HTTPException(status_code=500, detail="Error making user driver")
    
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



def get_driver_profile(driver_id: str, db: Session):
    driver = db.query(Drivers).filter(Drivers.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    comments = db.query(RiderDriverComment).filter(RiderDriverComment.driver_id == driver_id).all()
    comment_list = [
        Comment(
            comment=comment.comment,
            rating=comment.rating,
            name=db.query(Users).filter(Users.user_id == comment.user_id).first().name,
            photo_url=db.query(Users).filter(Users.user_id == comment.user_id).first().photo_url,
            date=db.query(Rides).filter(Rides.ride_id == comment.ride_id).first().ride_date
        ) for comment in comments
    ]

    profile_data = ProfileData(
        name=db.query(Users).filter(Users.user_id == driver.user_id).first().name,
        email=db.query(Users).filter(Users.user_id == driver.user_id).first().email,
        photo_url=db.query(Users).filter(Users.user_id == driver.user_id).first().photo_url,
        rating=driver.driver_rating,
        comments=comment_list
    )

    return profile_data


def get_rider_profile(user_id: str, db: Session):
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    comments = db.query(DriverRiderComment).filter(DriverRiderComment.user_id == user_id).all()
    comment_list = []
    for comment in comments:
        driver_as_user = db.query(Users).filter(Users.user_id == (db.query(Drivers).filter(Drivers.driver_id == comment.driver_id).user_id)).first()
        comment_list.append(
            Comment(
                comment=comment.comment,
                rating=comment.rating,
                name=driver_as_user.name,
                photo_url=driver_as_user.photo_url,
                date=db.query(Rides).filter(Rides.ride_id == comment.ride_id).first().date
            )
        )

    profile_data = ProfileData(
        name=user.name,
        email=user.email,
        photo_url=user.photo_url,
        rating=user.rider_rating,
        comments=comment_list
    )

    return profile_data


def comment_driver(driver_id: str, ride_id: str, comment: str, rating: int, current_user, db):
    driver = db.query(Drivers).filter(Drivers.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if rating < 0 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")

    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    comment_model = RiderDriverComment(
        comment=comment,
        rating=rating,
        user_id=current_user.user_id,
        driver_id=driver_id,
        ride_id=ride_id
    )

    try:
        db.add(comment_model)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error adding comment")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Comment added successfully"})


def comment_rider(user_id: str, ride_id: str, comment: str, rating: int, current_user, db):
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if rating < 0 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")

    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()

    if not driver:
        raise HTTPException(status_code=403, detail="User is not a driver")
    
    if ride.driver_id != driver.driver_id:
        raise HTTPException(status_code=403, detail="You are not the driver of this ride")
    

    comment_model = DriverRiderComment(
        comment=comment,
        rating=rating,
        user_id=user_id,
        driver_id=current_user.user_id,
        ride_id=ride_id
    )

    try:
        db.add(comment_model)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error adding comment")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Comment added successfully"})
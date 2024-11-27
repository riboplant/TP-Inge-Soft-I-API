from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import uuid4
from utils.imgBBAPI import upload_image
from schemas.users_schemas import UserData, ProfileData, Comment
from database.models import Users, Drivers, Vehicles, Drives, Rides, RiderDriverComment, DriverRiderComment



def get_user_by_id(user_id: str, db: Session):
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_driver_by_id(driver_id: str, db: Session):
    driver = db.query(Drivers).filter(Drivers.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


def get_driver_by_user(user_id: str, db: Session):
    driver = db.query(Drivers).filter(Drivers.user_id == user_id).first()
    if not driver:
        raise HTTPException(status_code=403, detail="User is not a driver")
    return driver


def validate_rating(rating: int):
    if rating < 0 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")


def update_db_record(record, db: Session, updates: dict):
    for key, value in updates.items():
        setattr(record, key, value)
    try:
        db.commit()
        db.refresh(record)
    except Exception:
        raise HTTPException(status_code=500, detail="Error updating database")


# Core functions
def get_user_data(current_user, db):
    user_model = get_user_by_id(current_user.user_id, db)
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()

    return UserData(
        name=user_model.name,
        email=user_model.email,
        address=user_model.address,
        dni=user_model.dni,
        photo_url=user_model.photo_url,
        is_driver=bool(driver),
        user_id=user_model.user_id
    )


async def edit_photo(base64Image: str, current_user, db):
    user_model = get_user_by_id(current_user.user_id, db)
    try:
        img = await upload_image(base64Image)
        update_db_record(user_model, db, {"photo_url": img["photo_url"], "delete_photo_url": img["delete_photo_url"]})
    except:
        raise HTTPException(status_code=500, detail="Error uploading or updating image")
    return {"photo_url": img["photo_url"]}


def delete_photo(current_user, db):
    user_model = get_user_by_id(current_user.user_id, db)
    update_db_record(user_model, db, {"photo_url": None, "delete_photo_url": None})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Image deleted successfully"})


def get_cars(current_user, db):
    driver = get_driver_by_user(current_user.user_id, db)
    vehicles = db.query(Vehicles).join(Drives).filter(Drives.driver_id == driver.driver_id).all()
    return [{"plate": vehicle.plate, "model": vehicle.model} for vehicle in vehicles]


def add_car(vehicle, current_user, db):
    driver = get_driver_by_user(current_user.user_id, db)
    plate = vehicle.plate.split(" ")[0]

    car = db.query(Vehicles).filter(Vehicles.plate == plate).first()
    if not car:
        new_vehicle = Vehicles(plate=plate, color=vehicle.color, model=vehicle.model, status="Unchecked")
        db.add(new_vehicle)
        db.commit()

    if not db.query(Drives).filter(Drives.plate == plate, Drives.driver_id == driver.driver_id).first():
        new_drive = Drives(plate=plate, driver_id=driver.driver_id)
        db.add(new_drive)
        db.commit()
    else:
        raise HTTPException(status_code=402, detail="Vehicle already added")
    
    return {"message": "Vehicle added successfully"}


def remove_car(plate: str, current_user, db):
    driver = get_driver_by_user(current_user.user_id, db)

    drive = db.query(Drives).filter(Drives.plate == plate.split(" ")[0], Drives.driver_id == driver.driver_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(drive)
    db.commit()

    remaining_drive = db.query(Drives).filter(Drives.plate == plate).first()
    ride = db.query(Rides).filter(Rides.car_plate == plate).first()

    if not remaining_drive and not ride:
        vehicle = db.query(Vehicles).filter(Vehicles.plate == plate).first()
        db.delete(vehicle)
        db.commit()

    return {"message": "Vehicle removed successfully"}


def make_driver(current_user, db):
    if db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first():
        raise HTTPException(status_code=403, detail="User is already a driver")
    
    driver_model = Drivers(
        user_id=current_user.user_id,
        driver_id=str(uuid4()),
        driving_license=0,
        driver_rating=0,
        status=0
    )
    db.add(driver_model)
    db.commit()
    return driver_model.driver_id


def edit_name(name: str, current_user, db):
    if not name or len(name) < 1:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    user_model = get_user_by_id(current_user.user_id, db)
    update_db_record(user_model, db, {"name": name})
    return {"name": name}


def get_driver_profile(driver_id: str, db: Session):
    driver = get_driver_by_id(driver_id, db)
    user = get_user_by_id(driver.user_id, db)
    comments = db.query(RiderDriverComment).filter(RiderDriverComment.driver_id == driver_id).all()

    comment_list = [
        Comment(
            comment=comment.comment,
            rating=comment.rating,
            name=get_user_by_id(comment.user_id, db).name,
            photo_url=get_user_by_id(comment.user_id, db).photo_url,
            comment_date=db.query(Rides).filter(Rides.ride_id == comment.ride_id).first().ride_date
        ) for comment in comments
    ]

    return ProfileData(
        name=user.name,
        email=user.email,
        photo_url=user.photo_url,
        avg_rating=int(sum(comment.rating for comment in comments) / len(comments)) if comments else 0,
        comments=comment_list
    )



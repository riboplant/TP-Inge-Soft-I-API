from fastapi import HTTPException, Depends, status, APIRouter
from app.schemas.users_schemas import User, UserCreate
from app.schemas.rides_schemas import Ride
from app.database.connect import engine, SessionLocal
from sqlalchemy.orm import Session
from app.controllers.auth import get_current_active_user
from app.database.models import models
from app.database.connect import Base
import sys
from uuid import uuid4

sys.path.append('..')

Base.metadata.create_all(bind=engine)



def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/test")
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        user_id=str(uuid4()),
        name=user.name,
        rider_rating=user.rider_rating,
        email=user.email,
        hashed_password=user.password,  # Recuerda hashear la contraseña aquí
        disabled=user.disabled,
        address=user.address,
        dni=user.dni,
        status=user.status,
        photo_id=user.photo_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/rides")
def read_api(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(models.Rides).all()

@router.get("/users")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Users).all() 


@router.post("/rides")
def create_ride(ride: Ride, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    ride_model = models.Rides()
    ride_model.ubication_from = ride.ubicationFrom
    ride_model.ubication_to = ride.ubicationTo
    ride_model.city_from = ride.city_from
    ride_model.city_to = ride.city_to
    ride_model.description = ride.description
    ride_model.car_model = ride.carModel
    ride_model.car_plate = ride.carPlate
    ride_model.date = ride.date
    ride_model.start_minimum_time = ride.start_minimum_time
    ride_model.start_maximum_time = ride.start_maximum_time
    ride_model.real_start_time = ride.real_start_time
    ride_model.real_end_time = ride.real_end_time
    ride_model.driver_id = ride.driver_id


    db.add(ride_model)
    db.commit()
    db.refresh(ride_model)

    return ride_model

@router.delete("/rides")
def delete_ride(ride_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):

    ride_model = db.query(models.Rides).filter(models.Rides.ride_id == ride_id).first()

    if ride_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {ride_id} : Does not exist"
        )
    
    db.query(models.Rides).filter(models.Rides.ride_id == ride_id).delete()
    db.commit()


@router.put("/users")
def edit_user(user_id: int, user:User, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # No es posible editar la password o el user_id pero eso esta bien por ahora
    user_model = db.query(models.Users).filter(models.Users.user_id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} : Does not exist"
        )
    
    user_model.name = user.name
    user_model.user_rating = user.user_rating
    user_model.email = user.email
    user_model.address = user.address
    user_model.dni = user.dni
    user_model.status = user.status
    user_model.photo_id = user.photo_id

    db.add(user_model)
    db.commit()

    return user
from fastapi import HTTPException, Depends, status, APIRouter
from schemas.users_schemas import User
from schemas.rides_schemas import Ride
from database.connect import engine, SessionLocal
from sqlalchemy.orm import Session
from routers.auth import get_current_active_user
from database.models import users_models, rides_models
from database.connect import Base
import sys
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

@router.get("/rides")
def read_api(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(rides_models.Rides).all()

@router.get("/users")
def read_api(db: Session = Depends(get_db)):
    return db.query(users_models.Users).all() 


@router.post("/rides")
def create_ride(ride: Ride, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    ride_model = rides_models.Rides()
    ride_model.ubication_from = ride.ubicationFrom
    ride_model.ubication_to = ride.ubicationTo
    ride_model.city_from = ride.city_from
    ride_model.city_to = ride.city_to
    ride_model.description = ride.description
    ride_model.car_model = ride.carModel
    ride_model.car_plate = ride.carPlate
    ride_model.price_person = ride.price_person
    ride_model.price_small_package = ride.price_small_package
    ride_model.price_medium_package = ride.price_medium_package
    ride_model.price_large_package = ride.price_large_package
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

    ride_model = db.query(rides_models.Rides).filter(rides_models.Rides.ride_id == ride_id).first()

    if ride_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {ride_id} : Does not exist"
        )
    
    db.query(rides_models.Rides).filter(rides_models.Rides.ride_id == ride_id).delete()
    db.commit()


@router.put("/users")
def edit_user(user_id: int, user:User, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # No es posible editar la password o el user_id pero eso esta bien por ahora
    user_model = db.query(users_models.Users).filter(users_models.Users.user_id == user_id).first()

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
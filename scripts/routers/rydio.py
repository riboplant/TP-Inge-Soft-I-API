from fastapi import HTTPException, Depends, status, APIRouter
from schemas import User, Ride
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from routers.auth import get_current_active_user
import models
import sys
import config
sys.path.append('..')

models.Base.metadata.create_all(bind=engine)



def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix="/rydio",
    tags=["rydio"]
)

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
    ride_model.description = ride.description
    ride_model.car_model = ride.carModel
    ride_model.car_plate = ride.carPlate
    ride_model.price = ride.price

    db.add(ride_model)
    db.commit()


@router.delete("/rides")
def delete_ride(ride_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):

    ride_model = db.query(models.Rides).filter(models.Rides.id == ride_id).first()

    if ride_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {ride_id} : Does not exist"
        )
    
    db.query(models.Rides).filter(models.Rides.id == ride_id).delete()
    db.commit()


@router.put("/users")
def edit_user(user_id: int, user:User, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} : Does not exist"
        )
    
    user_model.name = user.name
    user_model.rating = user.rating

    db.add(user_model)
    db.commit()

    return user
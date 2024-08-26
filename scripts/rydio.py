from typing import List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class User(BaseModel):
    name: str = Field(min_length=1)
    rating: float = Field(get=0, let=5)

class Ride(BaseModel):
    ubicationFrom: str = Field(min_length=1, max_length=100)
    ubicationTo: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    carModel: str = Field(min_length=1, max_length=50)
    carPlate: str = Field(min_length=1, max_length=10)
    price: float = Field(gt=0)


@app.get("/rides")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Rides).all()


@app.post("/rides")
def create_ride(ride: Ride, db: Session = Depends(get_db)):
    ride_model = models.Rides()
    ride_model.ubication_from = ride.ubicationFrom
    ride_model.ubication_to = ride.ubicationTo
    ride_model.description = ride.description
    ride_model.car_model = ride.carModel
    ride_model.car_plate = ride.carPlate
    ride_model.price = ride.price

    db.add(ride_model)
    db.commit()


@app.delete("/rides")
def delete_ride(ride_id: int, db: Session = Depends(get_db)):

    ride_model = db.query(models.Rides).filter(models.Rides.id == ride_id).first()

    if ride_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {ride_id} : Does not exist"
        )
    
    db.query(models.Rides).filter(models.Rides.id == ride_id).delete()
    db.commit()


@app.post("/users/register")
def register_user(user: User, db: Session = Depends(get_db)):
    user_model = models.Users()
    user_model.name = user.name
    user_model.rating = user.rating

    db.add(user_model)
    db.commit()

@app.put("/users")
def edit_user(user_id: int, user:User, db: Session = Depends(get_db)):
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
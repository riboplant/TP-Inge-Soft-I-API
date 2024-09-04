from fastapi import HTTPException, Depends, status, APIRouter
from app.controllers.auth import get_current_active_user
from app.schemas.rides_schemas import Ride, RideCreate, PriceSet, searchRideForPackage,searchRideForPerson
from app.schemas.users_schemas import User
from app.database.models.model import *
from sqlalchemy.orm import Session
from app.database.connect import Base, engine, SessionLocal
from app.services import rides_controller
from datetime import date
from pydantic import Field

router = APIRouter(
    prefix="/rides",
    tags=["rides"]
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

#buscar viajes para personas
@router.get("/people") 
async def get_people_ride(cityFrom: str, cityTo: str, date: date, persons:  int , samllPackages: int , mediumPackages: int, largePackages: int):
    return rides_controller.get_people_ride(cityFrom, cityTo, date, persons, samllPackages, mediumPackages, largePackages) 

#esto es para buscar viajes para paquetes
@router.get("/package")
async def get_package_ride(cityFrom: str, cityTo: str, date: date, samllPackages: int , mediumPackages: int , largePackages: int ):
    return rides_controller.get_package_ride(cityFrom, cityTo, date, samllPackages, mediumPackages, largePackages)


@router.get("/create")#tiene que estar logueado
async def create_ride(locationFrom: str, locationTo: str):#quien es el driver, ver manejo de sesiones.El driver es el usuario logueado en ese momento
    return rides_controller.get_prices(locationFrom, locationTo)#retorna los precios

@router.post("/create/detail")#tiene que estar logueado
async def create_ride(rideData):#quien es el driver, ver manejo de sesiones.El driver es el usuario logueado en ese momento
    return "Vemos que retorna, puede ser un codigo nomas y listo"#creo que hay que definir un schema para Ride

#esto sirve para que el formulario de edicion de un viaje nos pida todos los datos y despues los edite y nos llamen al edit_ride
@router.get("/ride{ride_id}") #tiene que estar logueado y el viaje debe ser suyo
async def get_ride(ride_id : int):
    return ""

@router.put("/edit/{ride_id}")#tiene que estar logueado y el viaje debe ser suyo
async def edit_ride(ride_id : int):#si ya te pasaste de la fecha te decimos que no podes editar
    return "Vemos que retorna, puede ser un codigo nomas y listo"#creo que hay que definir un schema para Ride

@router.delete("/delete/{ride_id}")#tiene que estar logueado y el viaje debe ser suyo
async def edit_ride(ride_id : int): # si ya te pasaste de la fecha te decimos que no podes borrar
        return "Lo borre/no lo borre"

@router.get("/history")#Los viajes tales que su fecha es menor a la actual. Tiene que estar logueado para acceder
async def my_rides_history():
     return ""

@router.get("/upcoming")#Los viajes tales que su fecha es mayor a la actual. Tiene que estar logueado para acceder
async def my_rides_history():
     return ""
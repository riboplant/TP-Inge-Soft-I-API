from fastapi import HTTPException, Depends, status, APIRouter
from controllers.auth import get_current_active_user
from schemas.rides_schemas import Ride, RideCreate, PriceSet, searchRideForPackage,searchRideForPerson
from schemas.users_schemas import User
from database.models.rides_models import Rides, Prices
from database.models.users_models import Users
from sqlalchemy.orm import Session
from database.connect import Base, engine, SessionLocal
from services import rides_controller


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
#hago un post porque hay tantos campos que puede que no entre en el query string
@router.post("/people") 
async def get_people_ride(parameters: searchRideForPerson):
    return rides_controller.get_people_ride(parameters) 

#esto es para buscar viajes para paquetes
@router.post("/package")
async def get_package_ride(parameters: searchRideForPackage):
    return rides_controller.get_package_ride(parameters)


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
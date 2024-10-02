from fastapi import HTTPException, Depends, status, APIRouter
from datetime import date
from sqlalchemy.orm import Session
from uuid import uuid4
from utils.locationIQAPI import get_coordinates
from controllers.auth import get_current_active_user
from services import rides

from schemas.rides_schemas import *
from schemas.users_schemas import *
from database.models import *
from database.connect import get_db




router = APIRouter(
    prefix="/rides",
    tags=["rides"]
)

#buscar viajes para personas
@router.get("/search") 
async def get_ride(city_from: str, city_to: str, date: date, people:  int , small_packages: int,  medium_packages: int, large_packages: int):
    return rides.get_ride(city_from, city_to, date, people, small_packages,  medium_packages, large_packages) 


#retorna los precios y -1 si no se encontro alguna de las ciudades
@router.get("/create")#tiene que estar logueado
async def create_ride(location_from: str, location_to: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.get_prices_and_cars(location_from, location_to,current_user, db)


@router.post("/create/detail")#tiene que estar logueado
async def create_ride(ride: RideCreate, price: PriceSet, plate: str , current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):#quien es el driver, ver manejo de sesiones.El driver es el usuario logueado en ese momento
    return rides.create_ride(ride, price, plate, current_user, db)


@router.get("/history/driver")
async def history_driver( current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
     return rides.history_driver(current_user, db)

@router.get("/upcoming/driver")
async def upcoming_driver( current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
     return rides.upcoming_driver(current_user, db)

@router.get("/history/rider")
async def history_rider( current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
     return rides.history_rider(current_user, db)

@router.get("/upcoming/rider")
async def my_rides_upcoming( current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
     return rides.upcoming_rider(current_user, db)


##VEEEEEEEEEEEEEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR

# #esto sirve para que el formulario de edicion de un viaje nos pida todos los datos y despues los edite y nos llamen al edit_ride
# @router.get("/ride{ride_id}") #tiene que estar logueado y el viaje debe ser suyo
# async def get_ride(ride_id : int):
#     return ""

# @router.put("/edit/{ride_id}")#tiene que estar logueado y el viaje debe ser suyo
# async def edit_ride(ride_id : int):#si ya te pasaste de la fecha te decimos que no podes editar
#     return "Vemos que retorna, puede ser un codigo nomas y listo"#creo que hay que definir un schema para Ride

# @router.delete("/delete/{ride_id}")#tiene que estar logueado y el viaje debe ser suyo
# async def edit_ride(ride_id : int): # si ya te pasaste de la fecha te decimos que no podes borrar
#         return "Lo borre/no lo borre"

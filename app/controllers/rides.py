from fastapi import HTTPException, Depends, status, APIRouter
from datetime import date
from sqlalchemy.orm import Session
from uuid import uuid4

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
@router.get("/people") 
async def get_people_ride(city_from: str, city_to: str, date: date, people:  int , small_packages: int , medium_packages: int, large_packages: int):
    return rides.get_people_ride(city_from, city_to, date, people, small_packages, medium_packages, large_packages) 

#esto es para buscar viajes para paquetes
@router.get("/package")
async def get_package_ride(city_from: str, city_to: str, date: date, small_packages: int , medium_packages: int , large_packages: int ):
    return rides.get_package_ride(city_from, city_to, date, small_packages, medium_packages, large_packages)


#retorna los precios y -1 si no se encontro alguna de las ciudades
@router.get("/create")#tiene que estar logueado
async def create_ride(location_from: str, location_to: str):
    return rides.get_prices(location_from, location_to)



@router.post("/create/detail")#tiene que estar logueado
async def create_ride(ride: RideCreate, price: PriceSet, plate: str , current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):#quien es el driver, ver manejo de sesiones.El driver es el usuario logueado en ese momento
    #Check if user is a driver, check that the car is from the user
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
         return {"User is not a driver"} # aca tenemos que ver de tirar un error http

    driver_id = driver.driver_id
    check_plate = db.query(Drives).filter(Drives.plate == plate, Drives.driver_id == driver_id).first()
    if not check_plate:
         return {"Car does not belong to the driver"} # aca tenemos que ver de tirar un error http

    ans = rides.create_ride(ride,price,plate,driver_id,current_user)

    if ans == -1:
        return {"Invalid city"} # ver de tirar una excepcion http
    
    return 0;#Todo bien 

   


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

# @router.get("/history")#Los viajes tales que su fecha es menor a la actual. Tiene que estar logueado para acceder
# async def my_rides_history():
#      return ""

# @router.get("/upcoming")#Los viajes tales que su fecha es mayor a la actual. Tiene que estar logueado para acceder
# async def my_rides_history():
#      return ""
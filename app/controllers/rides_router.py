from fastapi import HTTPException, Depends, status, APIRouter
from controllers.auth import get_current_active_user
from schemas.rides_schemas import Ride, RideCreate, PriceSet, searchRideForPackage,searchRideForPerson
from schemas.users_schemas import User
from database.models.rides_models import Rides, Prices
from database.models.users_models import Users, Drivers, Drives
from sqlalchemy.orm import Session
from database.connect import Base, engine, SessionLocal
from services import rides_controller
from uuid import uuid4

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
async def create_ride(ride: RideCreate, price: PriceSet, plate: str , current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):#quien es el driver, ver manejo de sesiones.El driver es el usuario logueado en ese momento
    #Check if user is a driver, check that the car is from the user
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
         return {"User is not a driver"}

    driver_id = driver.driver_id
    check_plate = db.query(Drives).filter(Drives.plate == plate, Drives.driver_id == driver_id).first()
    if not check_plate:
         return {"Car does not belong to the driver"}

    ride_model = Rides()
    ride_model.driver_id = driver_id
    ride_model.car_plate = plate
    ride_model.ride_id = str(uuid4())
    ride_model.ubication_from = ride.ubicationFrom
    ride_model.ubication_to = ride.ubicationTo
    ride_model.city_from = ride.city_from
    ride_model.city_to = ride.city_to
    ride_model.ride_date = ride.ride_date
    ride_model.start_minimum_time = ride.start_minimum_time
    ride_model.start_maximum_time = ride.start_maximum_time
    ride_model.real_end_time = None
    ride_model.real_start_time = None

    price_model = Prices()
    price_model.ride_id = ride_model.ride_id
    price_model.price_person = price.price_person
    price_model.price_small_package = price.price_small_package
    price_model.price_medium_package = price.price_medium_package
    price_model.price_large_package = price.price_large_package

    db.add(ride_model)
    db.commit()
    db.add(price_model)
    db.commit()


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
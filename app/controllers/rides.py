from fastapi import Depends, APIRouter
from datetime import date
from sqlalchemy.orm import Session

from controllers.auth import get_current_active_user
from services import rides
from schemas.rides_schemas import *
from schemas.users_schemas import User
from database.connect import get_db




router = APIRouter(
    prefix="/rides",
    tags=["rides"]
)

#buscar viajes para personas
@router.get("/search") 
async def get_ride(city_from: str, city_to: str, date: date, people:  int , small_packages: int,  medium_packages: int, large_packages: int, db: Session = Depends(get_db)):
    return rides.get_ride(city_from, city_to, date, people, small_packages,  medium_packages, large_packages, db) 


#retorna los precios y -1 si no se encontro alguna de las ciudades
@router.get("/create")#tiene que estar logueado
async def create_ride(location_from: str, location_to: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.get_prices_and_cars(location_from, location_to,current_user, db)


@router.post("/create/detail")#tiene que estar logueado
async def create_ride(ride: RideCreate, price: PriceSet, plate: str , current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):#quien es el driver, ver manejo de sesiones.El driver es el usuario logueado en ese momento
    print('pase')
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

@router.get("/detail/{ride_id}")
async def get_ride_detail(ride_id: str, db: Session = Depends(get_db)):
    return rides.get_ride_detail(ride_id, db)

@router.post("/join")
async def join_ride(data: JoinRideData, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.join_ride(data, current_user, db)

@router.get("/requests/pendings/{ride_id}")
async def get_requests_pendings(ride_id: str, current_user: User = Depends(get_current_active_user) ,db: Session = Depends(get_db)):
    return rides.get_requests_pendings(ride_id, current_user, db)

@router.put("/requests/isAccepted")
async def is_accepted(data: AcceptedData, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.is_accepted(data, current_user, db)
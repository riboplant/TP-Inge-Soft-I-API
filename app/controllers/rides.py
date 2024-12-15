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

@router.get("/search") 
async def get_ride(city_from: str, city_to: str, date: date, people:  int , small_packages: int,  medium_packages: int, large_packages: int, db: Session = Depends(get_db)):
    return rides.get_ride(city_from, city_to, date, people, small_packages,  medium_packages, large_packages, db) 


@router.get("/create")
async def create_ride(location_from: str, location_to: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.get_prices_and_cars(location_from, location_to,current_user, db)


@router.post("/create/detail")
async def create_ride(ride: RideCreate, price: PriceSet, plate: str , current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
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

@router.get("/today/rider_driver")
async def today_rider_driver( current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
     return rides.today_rider_driver(current_user, db)

@router.get("/search/detail/{ride_id}")
async def get_ride_search_detail(ride_id: str, db: Session = Depends(get_db)):
    return rides.get_ride_search_detail(ride_id, db)

@router.get("/rider/detail/{ride_id}")
async def get_rider_detail(ride_id: str,current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.get_rider_detail(ride_id, current_user, db)

@router.get("/driver/detail/{ride_id}")
async def get_driver_detail(ride_id: str,current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.get_driver_detail(ride_id, current_user, db)


@router.get("/driver/history/detail/{ride_id}")
async def get_driver_history_detail(ride_id: str,current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.get_driver_history_detail(ride_id, current_user, db)


@router.post("/join")
async def join_ride(data: JoinRideData, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await rides.join_ride(data, current_user, db)

@router.delete("/leave/{ride_id}")
async def leave_ride(ride_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await rides.leave_ride(ride_id, current_user, db)

@router.get("/requests/pendings/{ride_id}")
async def get_requests_pendings(ride_id: str, current_user: User = Depends(get_current_active_user) ,db: Session = Depends(get_db)):
    return rides.get_requests_pendings(ride_id, current_user, db)

@router.put("/requests/isAccepted")
async def is_accepted(data: AcceptedData, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await rides.is_accepted(data, current_user, db)

@router.post("/start/{ride_id}")
async def start_ride(ride_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await rides.start_ride(ride_id, current_user, db)

@router.post("/finish/{ride_id}")
async def finish_ride(ride_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return await rides.finish_ride(ride_id, current_user, db)

@router.delete("/cancel/{ride_id}")
async def cancel_ride(ride_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return rides.cancel_ride(ride_id, current_user, db)
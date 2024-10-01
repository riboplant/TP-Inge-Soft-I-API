from schemas.rides_schemas import *
from datetime import date
from pydantic import Field
from sqlalchemy import and_
from dotenv import load_dotenv
from uuid import uuid4
from decouple import config
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from datetime import datetime



from database.connect import get_db
from database.models import *
from utils.locationIQAPI import get_distance_between, get_coordinates


def get_ride(city_from: str, city_to: str, date: date, people:  int = Field(ge=0),small_packages: int = Field(ge=0),  medium_packages: int = Field(ge=0), large_packages: int = Field(ge=0)):
    ridesToRet = []

    # Obtén la sesión y consulta la base de datos
    with next(get_db()) as db_session:
        rides = db_session.query(Rides).filter(
            and_(
                Rides.city_from == city_from,
                Rides.city_to == city_to,
                Rides.ride_date == date,
                Rides.available_space_large_package >= large_packages,
                Rides.available_space_medium_package >= medium_packages,
                Rides.available_space_small_package >= small_packages,
                Rides.available_space_people >= people
            )
        ).all()  # Asegúrate de ejecutar la consulta con all() para obtener una lista

        for ride in rides:
            driver_user_id = db_session.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
            driver_as_user = db_session.query(Users).filter(Users.user_id == driver_user_id).first()
            priceSet = db_session.query(Prices).filter(Prices.ride_id == ride.ride_id).first()

            ride_to_return = rideToReturn(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                driver_name=driver_as_user.name,
                driver_photo=driver_as_user.photo_url if driver_as_user.photo_url is not None else "default_photo_url",
                price=_price(priceSet, people, small_packages, medium_packages, large_packages),
                date=ride.ride_date
            )


            ridesToRet.append(ride_to_return)
    
    return ridesToRet




def _get_price_set(distance:float):
    load_dotenv()
    
    fuel_price = float(config('FUEL_PRICE'))
    fuel_efficiency = float(config('FUEL_EFFICIENCY'))
    small_package_price = float(config('SMALL_PACKAGE_PRICE'))
    medium_package_price = float(config('MEDIUM_PACKAGE_PRICE'))
    large_package_price = float(config('LARGE_PACKAGE_PRICE'))
    
    ride_price = distance * fuel_efficiency * fuel_price
    
    set_prices = PriceSet(
    price_person=ride_price / 4, 
    price_small_package=small_package_price * distance, 
    price_medium_package=medium_package_price * distance, 
    price_large_package=large_package_price * distance
)

    return set_prices


def get_prices_and_cars(city_from: str, city_to: str, current_user, db):

    try:
        distance = get_distance_between(city_from,city_to)
    except:
        raise HTTPException(status_code=400, detail="Error getting distance between cities")
    
    priceSet = _get_price_set(distance)
    
    #Checking if user is driver
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=402, detail="User is not a driver")
    
    vehicles = db.query(Vehicles).join(Drives).filter(Drives.driver_id == driver.driver_id).all()
    
    vehicle_list = [{"plate": vehicle.plate, "model": vehicle.model} for vehicle in vehicles]
    
    return {
        "prices": priceSet,
        "cars": vehicle_list
    }
    


def prices_and_cars(ride: RideCreate, price: PriceSet, plate: str, driver_id:str, db: Session):

    ride_model = Rides()

    
    ride_model.ride_id = str(uuid4())
    try:
        ride_model.ubication_from = get_coordinates(ride.city_from)# ojo aca,estoy puede fallar si la version gratis de la api
        ride_model.ubication_to = get_coordinates(ride.city_to)    # tiene un limite de una llamada por segundo de ultima metemos un sleep aca. TESTEAAAR
    except:
        raise HTTPException(status_code=400, detail="Error getting coordinates")
    
    ride_model.car_plate = plate
    ride_model.driver_id = driver_id
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

    try:
        db.add(ride_model)
        db.commit()

        db.add(price_model)
        db.commit()
        
    except:
        raise HTTPException(status_code=400, detail="Error adding ride to database")
    
    return 0 


#cuando el time no este mas harcodeado lo tenemos que agregar en estos dos metodos para hacer la comparacion
def history_driver( current_user, db):
    rides_to_return = []
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=402, detail="User is not a driver")
    rides = db.query(Rides).filter(Rides.driver_id == driver.driver_id, Rides.ride_date <= datetime.now().date()).all()
    
    for ride in rides:
            prices = db.query(Prices).filter(Prices.ride_id == ride.ride_id).first()



            ride_to_return = HistoryOrUpcomingAsDriver(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                date=ride.ride_date,
                price= _total_price(ride.ride_id, prices, db)
            )



            rides_to_return.append(ride_to_return)
    
    return rides_to_return

def upcoming_driver( current_user, db):
    rides_to_return = []
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=402, detail="User is not a driver")
    rides = db.query(Rides).filter(Rides.driver_id == driver.driver_id, Rides.ride_date > datetime.now().date()).all()
    
    for ride in rides:

            ride_to_return = HistoryOrUpcomingAsDriver(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                date=ride.ride_date,
                price=_total_price(ride.ride_id, db)
            )


            rides_to_return.append(ride_to_return)
    
    return rides_to_return



def _price(priceSet: PriceSet, people: int, small_packages: int, medium_packages: int, large_packages: int):
    return priceSet.price_person * people + priceSet.price_large_package * large_packages + priceSet.price_medium_package * medium_packages + priceSet.price_small_package * small_packages

def _total_price(ride_id, set_prices, db):
    vec = db.query(Carrys).filter(Carrys.ride_id == ride_id).all()
    sum = 0
    for row in vec:
        sum += _price(set_prices, row.persons, row.small_packages, row.medium_packages, row.large_Packages)
    return sum
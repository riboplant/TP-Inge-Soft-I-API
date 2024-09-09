from schemas.rides_schemas import *
from datetime import date
from pydantic import Field
from sqlalchemy import and_
from dotenv import load_dotenv
from uuid import uuid4
from decouple import config




from database.connect import get_db
from database.models import *
from utils.locationIQAPI import get_distance_between, get_coordinates


def get_people_ride(city_from: str, city_to: str, date: date, people:  int = Field(ge=0), small_packages: int = Field(ge=0), medium_packages: int = Field(ge=0), large_packages: int = Field(ge=0)):

    ridesToRet = []
    index = 0

   # Obtén la sesión y consulta la base de datos
    with next(get_db()) as db_session:
        rides = db_session.query(Rides).filter(
            and_(
                Rides.city_from == city_from,
                Rides.city_to == city_to,
                Rides.date == date,
                Rides.available_space_large_package >= large_packages,
                Rides.available_space_medium_package >= medium_packages,
                Rides.available_space_small_package >= small_packages,
                Rides.available_space_people >= people
                
            )
        )
        for ride in rides:
            driver_user_id = db_session.query(Drivers).filter_by(Drivers.driver_id == ride.driver_id).user_id
            driver_as_user = db_session.query(Users).filter(Users.user_id == driver_user_id).first()
            priceSet = db_session.query(Prices).filter(Prices.ride_id == ride.ride_id).first()
            
            ridesToRet[index]=rideToReturn(
                ride.ride_id,
                ride.city_from,
                ride.city_to,
                driver_as_user.name,
                driver_as_user.photo_id,
                priceSet.price_person * people + priceSet.price_small_package * small_packages + priceSet.price_medium_package * medium_packages + priceSet.price_large_package * large_packages,
                ride.date,
                )
            index = index + 1
    return ridesToRet
    
    

def get_package_ride(city_from: str, city_to: str, date: date, small_packages: int = Field(ge=0), medium_packages: int = Field(ge=0), large_packages: int = Field(ge=0)):
    ridesToRet = []
    index = 0

   # Obtén la sesión y consulta la base de datos
    with next(get_db()) as db_session:
        rides = db_session.query(Rides).filter(
            and_(
                Rides.city_from == city_from,
                Rides.city_to == city_to,
                Rides.date == date,
                Rides.available_space_large_package >= large_packages,
                Rides.available_space_medium_package >= medium_packages,
                Rides.available_space_small_package >= small_packages,    
            )
        )
        for ride in rides:
            driver_user_id = db_session.query(Drivers).filter_by(Drivers.driver_id == ride.driver_id).user_id
            driver_as_user = db_session.query(Users).filter(Users.user_id == driver_user_id).first()
            priceSet = db_session.query(Prices).filter(Prices.ride_id == ride.ride_id).first()
            
            ridesToRet[index]=rideToReturn(
                ride.ride_id,
                ride.city_from,
                ride.city_to,
                driver_as_user.name,
                driver_as_user.photo_id,
                priceSet.price_small_package * small_packages + priceSet.price_medium_package * medium_packages + priceSet.price_large_package * large_packages,
                ride.date,
                )
            index = index + 1
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


def get_prices(city_from: str, city_to: str):

    try:
        distance = get_distance_between(city_from,city_to)
    except:
        print("Something was wrong")
        return None
    
    return _get_price_set(distance)
    


def create_ride(ride: RideCreate, price: PriceSet, plate: str, driver_id:str):

    db =get_db()

    ride_model = Rides()
    ride_model.driver_id = driver_id
    ride_model.car_plate = plate
    ride_model.ride_id = str(uuid4())
    try:
        ride_model.ubication_from = get_coordinates(ride.city_from)# ojo aca,estoy puede fallar si la version gratis de la api
        ride_model.ubication_to = get_coordinates(ride.city_to)    # tiene un limite de una llamada por segundo de ultima metemos un sleep aca. TESTEAAAR
    except:
        return -1
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
    
    return 0 
    
    
    
    
    

  
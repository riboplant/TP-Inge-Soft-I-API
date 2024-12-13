from datetime import date, datetime
from uuid import uuid4
import pytz

from decouple import config
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from database.models import *
from schemas.rides_schemas import *
from utils.locationIQAPI import get_distance_between, get_coordinates
from utils.notifications import send_notification
import traceback
from services.users import get_cars

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




def get_ride(city_from, city_to, date, people,small_packages,  medium_packages, large_packages, db):
    ridesToRet = []
    
    rides = db.query(Rides).filter(
        Rides.city_from == city_from,
        Rides.city_to == city_to,
        Rides.ride_date == date,
        Rides.available_space_large_package >= large_packages,
        Rides.available_space_medium_package >= medium_packages,
        Rides.available_space_small_package >= small_packages,
        Rides.available_space_people >= people,
        or_(
            and_(Rides.start_maximum_time > datetime.now().time(), Rides.ride_date == datetime.now().date()),
            Rides.ride_date > datetime.now().date()  
        )
    ).all() 

    for ride in rides:
        driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
        driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
        priceSet = db.query(Prices).filter(Prices.ride_id == ride.ride_id).first()

        ride_to_return = rideToReturn(
            ride_id=ride.ride_id,
            city_from=ride.city_from,
            city_to=ride.city_to,
            driver_name=driver_as_user.name,
            driver_photo=driver_as_user.photo_url if driver_as_user.photo_url is not None else '',
            price=_price(priceSet, people, small_packages, medium_packages, large_packages),
            date=ride.ride_date,
            state=None
        )

        ridesToRet.append(ride_to_return)
    
    return ridesToRet


def get_prices_and_cars(city_from: str, city_to: str, current_user, db):

    try:
        distance = get_distance_between(city_from,city_to)
    except:
        raise HTTPException(status_code=400, detail="Error getting distance between cities")
    
    priceSet = _get_price_set(distance)
    

    return {
        "prices": priceSet,
        "cars": get_cars(current_user, db)
    }
    


def create_ride(ride: RideCreate, price: PriceSet, plate: str, current_user, db):
#Check if user is a driver, check that the car is from the user

    if plate is None or plate == '':
        raise HTTPException(status_code=400, detail="Plate is required")
    
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
         raise HTTPException(status_code=402, detail="User is not a driver")
    driver_id = driver.driver_id
    check_plate = db.query(Drives).filter(Drives.plate == plate, Drives.driver_id == driver_id).first()
    if not check_plate:
         raise HTTPException(status_code=400, detail="Car does not belong to the driver")

    ride_model = Rides(
        driver_id = driver_id,
        car_plate = plate,
        ride_id = str(uuid4()),
        ubication_from = get_coordinates(ride.city_to) ,
        ubication_to = get_coordinates(ride.city_to) ,
        city_from = ride.city_from,
        city_to = ride.city_to,
        ride_date = ride.ride_date,
        start_minimum_time = ride.start_minimum_time,
        start_maximum_time = ride.start_maximum_time,
        real_end_time = None,
        real_start_time = None,
        available_space_people = ride.available_space_people,
        available_space_small_package = ride.available_space_small_package,
        available_space_medium_package = ride.available_space_medium_package,
        available_space_large_package = ride.available_space_large_package
    )
    price_model = Prices(
        ride_id = ride_model.ride_id,
        price_person = price.price_person,
        price_small_package = price.price_small_package,
        price_medium_package = price.price_medium_package,
        price_large_package = price.price_large_package
    )

    try:
        db.add(ride_model)
        db.commit()
        
    except:
        raise HTTPException(status_code=500, detail="Error creating ride")
    
    try:     
        db.add(price_model)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error creating prices")
    
    return JSONResponse(status_code=200, content={"message": "Success"})



def history_driver( current_user, db):
    rides_to_return = []
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=402, detail="User is not a driver")
    rides = db.query(Rides).filter(Rides.driver_id == driver.driver_id, Rides.ride_date <= datetime.now().date(), Rides.real_end_time != None).all()
    
    for ride in rides:
            prices = db.query(Prices).filter(Prices.ride_id == ride.ride_id).first()
            status = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'pending').first()
            
            persons=0
            packages=0
            price = 0

            carrys = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'accepted').all()
            for carry in carrys:
                persons += carry.persons
                packages += carry.small_packages + carry.medium_packages + carry.large_Packages
                price += _price(prices, carry.persons, carry.small_packages, carry.medium_packages, carry.large_Packages)

            
            state = 'pending'
            if status is None :
                 state = None

            ride_to_return = HistoryOrUpcomingAsDriver(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                date=ride.ride_date,
                price= price,
                state=state,
                persons=persons,
                packages=packages,
                start_time=ride.start_minimum_time,
                real_end_time=ride.real_end_time,
                real_start_time=ride.real_start_time
            )



            rides_to_return.append(ride_to_return)
    
    return rides_to_return

def upcoming_driver( current_user, db):
    rides_to_return = []
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()
    if not driver:
        raise HTTPException(status_code=402, detail="User is not a driver")
    rides = db.query(Rides).filter(Rides.driver_id == driver.driver_id, Rides.ride_date >= datetime.now().date(), Rides.real_end_time == None).all()
    
    for ride in rides:
            prices = db.query(Prices).filter(Prices.ride_id == ride.ride_id).first()
            status = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'pending').first()
            
            persons=0
            packages=0
            price = 0

            carrys = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'accepted').all()
            for carry in carrys:
                persons += carry.persons
                packages += carry.small_packages + carry.medium_packages + carry.large_Packages
                price += _price(prices, carry.persons, carry.small_packages, carry.medium_packages, carry.large_Packages)

            
            state = 'pending'
            if status is None :
                 state = None

            ride_to_return = HistoryOrUpcomingAsDriver(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                date=ride.ride_date,
                price= price,
                state=state,
                persons=persons,
                packages=packages,
                start_time=ride.start_minimum_time,
                real_end_time=ride.real_end_time,
                real_start_time=ride.real_start_time
            )



            rides_to_return.append(ride_to_return)
    
    return rides_to_return



def history_rider( current_user, db):
    rides_to_return = []
   
    carrys = db.query(Carrys).filter(Carrys.user_id == current_user.user_id, Carrys.state == 'accepted').all()
    
    for carry in carrys:
            ride = db.query(Rides).filter(Rides.ride_id == carry.ride_id, Rides.ride_date <= datetime.now().date(), Rides.real_end_time != None).first()
            if ride is None:
                continue
            
            driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
            driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
            priceSet = db.query(Prices).filter(Prices.ride_id == ride.ride_id).first()

            ride_to_return = rideToReturn(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                driver_name=driver_as_user.name,
                driver_photo=driver_as_user.photo_url if driver_as_user.photo_url is not None else '',
                price=_price(priceSet, carry.persons, carry.small_packages, carry.medium_packages, carry.large_Packages),
                date=ride.ride_date,
                state=None,
                start_time=ride.start_minimum_time,
                real_end_time=ride.real_end_time,
                real_start_time=ride.real_start_time
            )

            rides_to_return.append(ride_to_return)
    
    return rides_to_return


def upcoming_rider( current_user, db):
    rides_to_return = []
   
    carrys = db.query(Carrys).filter(Carrys.user_id == current_user.user_id).all()
    
    for carry in carrys:
            ride = db.query(Rides).filter(Rides.ride_id == carry.ride_id, Rides.ride_date >= datetime.now().date(), Rides.real_end_time == None).first()
            if ride is None:
                continue
            
            driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
            driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
            priceSet = db.query(Prices).filter(Prices.ride_id == ride.ride_id).first()

            ride_to_return = rideToReturn(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                driver_name=driver_as_user.name,
                driver_photo=driver_as_user.photo_url if driver_as_user.photo_url is not None else '',
                price=_price(priceSet, carry.persons, carry.small_packages, carry.medium_packages, carry.large_Packages),
                date=ride.ride_date,
                state=carry.state,
                start_time=ride.start_minimum_time,
                real_end_time=ride.real_end_time,
                real_start_time=ride.real_start_time,
                paid=carry.payment_id is not None
            )

            rides_to_return.append(ride_to_return)
    
    return rides_to_return


def today_rider_driver( current_user, db):
    rides_to_return = []
   
    carrys = db.query(Carrys).filter(Carrys.user_id == current_user.user_id, Carrys.state == 'accepted').all()
    
    for carry in carrys:
            ride = db.query(Rides).filter(Rides.ride_id == carry.ride_id, Rides.ride_date == datetime.now().date(), Rides.real_end_time == None).first()
            if ride is None:
                continue
            
            ride_to_return = TodayRides(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                packages=carry.small_packages + carry.medium_packages + carry.large_Packages,
                people=carry.persons,
                type='rider',
                start_time=ride.start_minimum_time,
                real_start_time=ride.real_start_time)

            rides_to_return.append(ride_to_return)
    
    driver = db.query(Drivers).filter(Drivers.user_id == current_user.user_id).first()

    rides = db.query(Rides).filter(Rides.driver_id == driver.driver_id, Rides.ride_date == datetime.now().date(), Rides.real_end_time == None).all()

    for ride in rides:
            carrys = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'accepted').all()
            persons=0
            packages=0
            for carry in carrys:
                persons += carry.persons
                packages += carry.small_packages + carry.medium_packages + carry.large_Packages
            
            ride_to_return = TodayRides(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                packages=packages,
                people=persons,
                type='driver',
                start_time=ride.start_minimum_time,
                real_start_time=ride.real_start_time)

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


def get_ride_search_detail(ride_id, db):
     
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    car = db.query(Vehicles).filter(Vehicles.plate == ride.car_plate).first()
    driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
    driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
    prices = db.query(Prices).filter(Prices.ride_id == ride_id).first()
    
    status = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'pending').first()     
    state = 'pending'
    if status is None :
        state = None

    ride_to_return = RideDetailToReturn(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                driver_name=driver_as_user.name,
                driver_photo=driver_as_user.photo_url if driver_as_user.photo_url is not None else '',
                price=0,
                date=ride.ride_date,
                state=state,
                available_space_persons=ride.available_space_people,
                available_space_small_package=ride.available_space_small_package,
                available_space_medium_package=ride.available_space_medium_package,
                available_space_large_package=ride.available_space_large_package,
                car_model=car.model,
                car_plate=car.plate,
                driver_id=ride.driver_id,
                price_person=prices.price_person,
                price_small_package=prices.price_small_package,
                price_medium_package=prices.price_medium_package,
                price_large_package=prices.price_large_package,
                start_maximum_time=ride.start_maximum_time,
                start_minimum_time=ride.start_minimum_time
            )

    return ride_to_return


def get_rider_detail(ride_id, current_user, db):
     
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    car = db.query(Vehicles).filter(Vehicles.plate == ride.car_plate).first()
    driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
    driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
    prices = db.query(Prices).filter(Prices.ride_id == ride_id).first()

    carry = db.query(Carrys).filter(Carrys.ride_id == ride_id, Carrys.user_id == current_user.user_id).first()
    naive_now = datetime.now(pytz.UTC)
    ride_to_return = RideDetailUpcomingRider(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                driver_name=driver_as_user.name,
                driver_photo=driver_as_user.photo_url if driver_as_user.photo_url is not None else '',
                price=_price(prices, carry.persons, carry.small_packages, carry.medium_packages, carry.large_Packages),
                date=ride.ride_date,
                state = carry.state if (
                    ride.ride_date > naive_now.date() or 
                    (ride.ride_date == naive_now.date() and ride.start_maximum_time.replace(tzinfo=None) > naive_now.time())
                ) else None,
                space_persons=carry.persons,
                space_small_package=carry.small_packages,
                space_medium_package=carry.medium_packages,
                space_large_package=carry.large_Packages,
                car_model=car.model,
                car_plate=car.plate,
                driver_id=ride.driver_id,
                start_maximum_time=ride.start_maximum_time,
                start_minimum_time=ride.start_minimum_time,
                paid=carry.payment_id is not None
            )

    return ride_to_return

def get_driver_detail(ride_id,current_user, db):
     
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    car = db.query(Vehicles).filter(Vehicles.plate == ride.car_plate).first()
    driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
    driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
    prices = db.query(Prices).filter(Prices.ride_id == ride_id).first()
    
    if driver_as_user.user_id != current_user.user_id:
        raise HTTPException(status_code=401, detail="User is not the driver of the ride")

    status = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'pending').first()     
    state = 'pending'
    if status is None :
        state = None

    carrys = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'accepted').all()

    riders = []

    for carry in carrys:
        user = db.query(Users).filter(Users.user_id == carry.user_id).first()
        chat = db.query(Chat).filter(
            or_(
                (Chat.user1_id == driver_as_user.user_id) & (Chat.user2_id == user.user_id),
                (Chat.user2_id == driver_as_user.user_id) & (Chat.user1_id == user.user_id)
            )
            ).first()
        riders.append(UserForListOfRiders(
            user_id=user.user_id,
            name=user.name,
            photo_url=user.photo_url if user.photo_url is not None else '',
            chat_id=chat.chat_id if chat is not None else ''
        ))
    
    ride_to_return = RideDetailUpcomingDriver(
                ride_id=ride.ride_id,
                city_from=ride.city_from,
                city_to=ride.city_to,
                driver_name=driver_as_user.name,
                driver_photo=driver_as_user.photo_url if driver_as_user.photo_url is not None else '',
                price=0,
                date=ride.ride_date,
                state=state,
                available_space_persons=ride.available_space_people,
                available_space_small_package=ride.available_space_small_package,
                available_space_medium_package=ride.available_space_medium_package,
                available_space_large_package=ride.available_space_large_package,
                car_model=car.model,
                car_plate=car.plate,
                driver_id=ride.driver_id,
                price_person=prices.price_person,
                price_small_package=prices.price_small_package,
                price_medium_package=prices.price_medium_package,
                price_large_package=prices.price_large_package,
                start_maximum_time=ride.start_maximum_time,
                start_minimum_time=ride.start_minimum_time,
                real_start_time=ride.real_start_time,
                real_end_time=ride.real_end_time,
                riders=riders
            )

    return ride_to_return

def get_driver_history_detail(ride_id, current_user, db):
     
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    car = db.query(Vehicles).filter(Vehicles.plate == ride.car_plate).first()
    prices = db.query(Prices).filter(Prices.ride_id == ride_id).first()

    persons=0
    small_packages=0
    medium_packages=0
    large_packages=0

    carrys = db.query(Carrys).filter(Carrys.ride_id == ride.ride_id, Carrys.state == 'accepted').all()
    for carry in carrys:
        persons += carry.persons
        small_packages += carry.small_packages
        medium_packages += carry.medium_packages
        large_packages += carry.large_Packages
    
    riders = []

    for carry in carrys:
        user = db.query(Users).filter(Users.user_id == carry.user_id).first()
        chat = db.query(Chat).filter(
            or_(
                (Chat.user1_id == current_user.user_id) & (Chat.user2_id == user.user_id),
                (Chat.user2_id == current_user.user_id) & (Chat.user1_id == user.user_id)
            )
            ).first()
        riders.append(UserForListOfRiders(
            user_id=user.user_id,
            name=user.name,
            photo_url=user.photo_url if user.photo_url is not None else '',
            chat_id=chat.chat_id if chat is not None else ''
        ))

    ride_to_return = RideDetailHistoryDriver(
                city_from=ride.city_from,
                city_to=ride.city_to,
                price=_total_price(ride_id, prices,db),
                date=ride.ride_date,
                start_maximum_time=ride.start_maximum_time,
                start_minimum_time=ride.start_minimum_time,
                persons=persons,
                small_package=small_packages,
                medium_package=medium_packages,
                large_package=large_packages,
                car_model=car.model,
                car_plate=car.plate,
                riders=riders  
            )

    return ride_to_return

async def join_ride(data: JoinRideData, user,db):

    ride = db.query(Rides).filter(Rides.ride_id == data.ride_id).first()
    if not ride:
        raise HTTPException(status_code=400, detail="Ride not found")
    
    if ride.available_space_people < data.people or ride.available_space_small_package < data.small_packages or ride.available_space_medium_package < data.medium_packages or ride.available_space_large_package < data.large_packages:
        raise HTTPException(status_code=400, detail="Not enough space in the ride")
    
    if data.people == 0 and data.small_packages == 0 and data.medium_packages == 0 and data.large_packages == 0:
        raise HTTPException(status_code=400, detail="You must carry at least one person or package")  

    driver_as_user = db.query(Users).filter(Users.user_id == db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id).first()

    try:
        await send_notification(driver_as_user.user_id, "Nueva solicitud!", f"{user.name} quiere unirse a tu viaje.")
    except:
        print("Error sending notification:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error sending notification")

    carry = Carrys(
        ride_id = data.ride_id,
        user_id = user.user_id,
        persons = data.people,
        small_packages = data.small_packages,
        medium_packages = data.medium_packages,
        large_Packages = data.large_packages,
        state = 'pending'
    )
    
    try:
        db.add(carry)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error joining ride")
    
    try:
        setattr(ride, 'available_space_people', ride.available_space_people - data.people)
        setattr(ride, 'available_space_small_package', ride.available_space_small_package - data.small_packages)
        setattr(ride, 'available_space_medium_package', ride.available_space_medium_package - data.medium_packages)
        setattr(ride, 'available_space_large_package', ride.available_space_large_package - data.large_packages)
        db.commit()
    except:
        db.delete(carry)
        db.commit()
        raise HTTPException(status_code=500, detail="Error updating ride")


    return JSONResponse(status_code=200, content={"message": "Success"})

async def leave_ride(ride_id, current_user, db):
    carry = db.query(Carrys).filter(Carrys.ride_id == ride_id, Carrys.user_id == current_user.user_id).first()
    if not carry:
        raise HTTPException(status_code=400, detail="Request not found")
    
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()

    if (ride.ride_date - datetime.now().date()).days < 1:
        raise HTTPException(status_code=400, detail="Cannot cancel ride within 24 hours of start time")
    
    if carry.payment_id is not None:
        raise HTTPException(status_code=400, detail="Cannot cancel ride after payment has been made")

    driver_as_user = db.query(Users).filter(Users.user_id == db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id).first()

    try:
        await send_notification(driver_as_user.user_id, "Solicitud cancelada!", f"{current_user.name} canceló su solicitud.")
    except:
        raise HTTPException(status_code=500, detail="Error sending notification")
    
    try:
        db.delete(carry)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error leaving ride")
    
    try:
        setattr(ride, 'available_space_people', ride.available_space_people + carry.persons)
        setattr(ride, 'available_space_small_package', ride.available_space_small_package + carry.small_packages)
        setattr(ride, 'available_space_medium_package', ride.available_space_medium_package + carry.medium_packages)
        setattr(ride, 'available_space_large_package', ride.available_space_large_package + carry.large_Packages)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error updating ride")
    
    return JSONResponse(status_code=200, content={"message": "Success"})

def get_requests_pendings(ride_id,current_user, db):

    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
    driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
    if driver_as_user.user_id != current_user.user_id:
        raise HTTPException(status_code=401, detail="User is not the driver of the ride")

    requests = db.query(Carrys).filter(Carrys.ride_id == ride_id, Carrys.state == 'pending').all()
    requests_to_return = []
    for request in requests:
        user = db.query(Users).filter(Users.user_id == request.user_id).first()
        
        request_to_return = RequestToReturn(
            user_id = user.user_id,
            user_name = user.name,
            user_photo = user.photo_url if user.photo_url is not None else '',
            people = request.persons,
            small_packages = request.small_packages,
            medium_packages = request.medium_packages,
            large_packages = request.large_Packages
        )
        requests_to_return.append(request_to_return)
    
    return requests_to_return


async def is_accepted(data, current_user, db):
    
    ride = db.query(Rides).filter(Rides.ride_id == data.ride_id).first()
    driver_user_id = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first().user_id
    driver_as_user = db.query(Users).filter(Users.user_id == driver_user_id).first()
    if driver_as_user.user_id != current_user.user_id:
        raise HTTPException(status_code=401, detail="User is not the driver of the ride")
    
    carry = db.query(Carrys).filter(Carrys.ride_id == data.ride_id, Carrys.user_id == data.user_id).first()
    if not carry:
        raise HTTPException(status_code=400, detail="Request not found")
    
    if data.is_accepted:
        setattr(carry, 'state', 'accepted')
        try:
            await send_notification(carry.user_id, "Solicitud aceptada!", f"{driver_as_user.name} aceptó tu solicitud.")
        except:
            raise HTTPException(status_code=880, detail="Error sending notification")
        
    else:
        try:
            await send_notification(carry.user_id, "Solicitud rechazada!", f"{driver_as_user.name} rechazó tu solicitud.")
        except:
            raise HTTPException(status_code=880, detail="Error sending notification")
        setattr(carry, 'state', 'dismissed')
        setattr(ride, 'available_space_people', ride.available_space_people + carry.persons)
        setattr(ride, 'available_space_small_package', ride.available_space_small_package + carry.small_packages)
        setattr(ride, 'available_space_medium_package', ride.available_space_medium_package + carry.medium_packages)
        setattr(ride, 'available_space_large_package', ride.available_space_large_package + carry.large_Packages)
    
    try:
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error updating request")
    
    return JSONResponse(status_code=200, content={"message": "Success"})



async def start_ride(ride_id: str, current_user, db):
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=400, detail="Ride not found")
    
    driver = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first()
    if driver.user_id != current_user.user_id:
        raise HTTPException(status_code=401, detail="User is not the driver of the ride")
    
    if ride.real_start_time is not None:
        raise HTTPException(status_code=400, detail="Ride has already started")
    
    aceptedCarrys = db.query(Carrys).filter(Carrys.ride_id == ride_id, Carrys.state == 'accepted').all()

    for carry in aceptedCarrys:
        user = db.query(Users).filter(Users.user_id == carry.user_id).first()
        try:
            await send_notification(user.user_id, "Viaje iniciado!", "El viaje ha comenzado.")
        except:
            raise HTTPException(status_code=500, detail="Error sending notification")


    pendingCarrys = db.query(Carrys).filter(Carrys.ride_id == ride_id, Carrys.state == 'pending').all()

    for carry in pendingCarrys:
        try:
            setattr(carry, 'state', 'dismissed')
            db.commit()
        except:
            raise HTTPException(status_code=489, detail="Error updating request")

    current_time = datetime.now().time()
    try:
        setattr(ride, 'real_start_time', current_time)
        db.commit()
    except:
        raise HTTPException(status_code=430, detail="Error starting ride")
    db.commit()
    
    return {"real_start_time": current_time}


def finish_ride(ride_id: str, current_user, db):
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=400, detail="Ride not found")
    
    driver = db.query(Drivers).filter(Drivers.driver_id == ride.driver_id).first()
    if driver.user_id != current_user.user_id:
        raise HTTPException(status_code=401, detail="User is not the driver of the ride")
    
    if ride.real_start_time is None:
        raise HTTPException(status_code=400, detail="Ride has not started yet")
    
    if ride.real_end_time is not None:
        raise HTTPException(status_code=400, detail="Ride has already finished")
    
    try:
        current_time = datetime.now().time()
        setattr(ride, 'real_end_time', current_time)
        db.commit()
    except:
        raise HTTPException(status_code=500, detail="Error finishing ride")
    
    return JSONResponse(status_code=200, content={"message": "Ride finished successfully"})
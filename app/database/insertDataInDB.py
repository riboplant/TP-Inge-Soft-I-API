import uuid
from datetime import date, time, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connect import SessionLocal
from database.models.model import Users, Vehicles,Drivers,Rides,Carrys,Prices

session = SessionLocal()



def generate_uuid():
    return str(uuid.uuid4())
users = [
    Users(user_id=generate_uuid(), name="Alice Johnson", rider_rating=4.9, email="alice.johnson@example.com",
          hashed_password="hashedpassword3", disabled=False, address="789 Pine Street", dni=23456789,
          status="active", photo_id=3),
    Users(user_id=generate_uuid(), name="Bob Brown", rider_rating=4.4, email="bob.brown@example.com",
          hashed_password="hashedpassword4", disabled=False, address="321 Maple Road", dni=98765432,
          status="active", photo_id=4)
]

# Crear nuevos vehículos
vehicles = [
    Vehicles(plate="LMN456", model="Ford Focus", color="Green", status="Available"),
    Vehicles(plate="OPQ012", model="Chevrolet Malibu", color="Black", status="Unavailable")
]

# Crear nuevos conductores
drivers = [
    Drivers(driver_id=generate_uuid(), user_id=users[0].user_id, driving_license=789012, driver_rating=4.7, status="active"),
    Drivers(driver_id=generate_uuid(), user_id=users[1].user_id, driving_license=210987, driver_rating=4.5, status="inactive")
]

# Crear 20 viajes con información variada
rides = []
for i in range(20):
    ride_date = date(2024, 9, 1) + timedelta(days=i % 10)  # Variar las fechas de los viajes
    start_time = time(random.randint(0, 23), random.randint(0, 59))  # Hora aleatoria
    end_time = time((start_time.hour + 1) % 24, (start_time.minute + 30) % 60)  # Hora de finalización estimada
    
    rides.append(
        Rides(
            ride_id=generate_uuid(),
            ubication_from=f"Location {chr(65 + i % 5)}",
            ubication_to=f"Location {chr(66 + i % 5)}",
            car_plate=random.choice([vehicle.plate for vehicle in vehicles]),
            driver_id=random.choice([driver.driver_id for driver in drivers]),
            ride_date=ride_date,
            start_minimum_time=start_time,
            start_maximum_time=end_time,
            real_end_time=None,
            real_start_time=None,
            city_from=f"City {chr(65 + i % 5)}",
            city_to=f"City {chr(66 + i % 5)}"
        )
    )

# Crear algunos carrys
carrys = []
for ride in rides:
    carrys.append(
        Carrys(
            ride_id=ride.ride_id,
            user_id=random.choice([user.user_id for user in users]),
            persons=random.randint(1, 3),
            small_packages=random.randint(0, 2),
            medium_packages=random.randint(0, 2),
            large_Packages=random.randint(0, 1)
        )
    )

# Crear algunos precios
prices = []
for ride in rides:
    prices.append(
        Prices(
            ride_id=ride.ride_id,
            price_person=random.uniform(10.0, 30.0),
            price_small_package=random.uniform(5.0, 10.0),
            price_medium_package=random.uniform(10.0, 15.0),
            price_large_package=random.uniform(15.0, 25.0)
        )
    )


def insertData():
    session.add_all(users)
    session.commit()
    session.add_all(vehicles)
    session.commit()
    session.add_all(drivers)
    session.commit()
    session.add_all(rides)
    session.commit()
    session.add_all(carrys)
    session.commit()
    session.add_all(prices)
    session.commit()
    session.close()

    return 0




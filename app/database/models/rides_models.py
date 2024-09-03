from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time
from database.connect import Base


class Rides(Base):
    __tablename__ = "rides"

    ride_id = Column(Integer, primary_key=True, index=True)
    ubication_from = Column(String)
    ubication_to = Column(String)
    city_from = Column(String)
    city_to = Column(String)
    car_plate = Column(String)
    driver_id = Column(Integer)
    date = Column(Date)
    start_minimum_time = Column(Time)
    start_maximum_time = Column(Time)
    real_start_time = Column(Time)
    real_end_time = Column(Time)


class Carrys(Base):
    __tablename__ = "carrys"

    ride_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, primary_key=True, index=True)
    persons = Column(Integer)
    small_packages = Column(Integer)
    medium_packages = Column(Integer)
    large_Packages = Column(Integer)


class Prices(Base):
    __tablename__ = "prices"

    ride_id = Column(Integer, primary_key=True, index=True)
    price_person = Column(Float)
    price_small_package = Column(Float)
    price_medium_package = Column(Float)
    price_large_package = Column(Float)
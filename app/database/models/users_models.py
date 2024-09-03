from sqlalchemy import Column, Integer, String, Float, Boolean
from database.connect import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    rider_rating = Column(Float)
    email = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean)
    address = Column(String)
    dni = Column(Integer)
    status = Column(String)
    photo_id = Column(Integer)

class Drivers(Base):
    __tablename__ = "drivers"

    user_id = Column(Integer)
    driving_license = Column(Integer)
    driver_rating = Column(Float)
    driver_id = Column(Integer, primary_key=True, index=True)
    status = Column(String)

class Vehicle(Base):
    __tablename__ = "vehicles"

    plate = Column(String, primary_key=True)
    model = Column(String)
    color = Column(String)
    status = Column(String)

class Drives(Base):
    __tablename__ = "drives"

    driver_id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, primary_key=True, index=True)



from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    rating = Column(Float)
    email = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean)
    
    
class Rides(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    ubication_from = Column(String)
    ubication_to = Column(String)
    description = Column(String)
    car_model = Column(String)
    car_plate = Column(String)
    price = Column(Float)




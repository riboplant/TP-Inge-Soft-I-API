from sqlalchemy import Column, Integer, String, Float
from database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    rating = Column(Float)
    
    
class Rides(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    ubication_from = Column(String)
    ubication_to = Column(String)
    description = Column(String)
    car_model = Column(String)
    car_plate = Column(String)
    price = Column(Float)




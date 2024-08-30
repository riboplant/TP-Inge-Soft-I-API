from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base


class Rides(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    ubication_from = Column(String)
    ubication_to = Column(String)
    description = Column(String)
    car_model = Column(String)
    car_plate = Column(String)
    price = Column(Float)
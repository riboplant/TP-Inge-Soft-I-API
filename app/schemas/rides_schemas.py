from pydantic import BaseModel, Field
from typing import Optional

class Ride(BaseModel):
    ride_id: int = Field(ge=0)
    ubicationFrom: str = Field(min_length=1, max_length=100)
    ubicationTo: str = Field(min_length=1, max_length=100)
    city_from: str = Field(min_length=1, max_length=100)
    city_to: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    carModel: str = Field(min_length=1, max_length=50)
    carPlate: str = Field(min_length=1, max_length=10)
    driver_id: int = Field(ge=0)
    price_person: int = Field(gt=0)
    price_small_package: int = Field(gt=0)
    price_medium_package: int = Field(gt=0)
    price_large_package: int = Field(gt=0)
    date: str = Field(min_length=8, max_length=10)
    start_minimum_time: str = Field(min_length=7, max_length=14)
    start_maximum_time: str = Field(min_length=7, max_length=14)
    real_start_time: str = Field(min_length=7, max_length=14)
    real_end_time: str = Field(min_length=7, max_length=14)

class Carry(BaseModel):
    ride_id: int = Field(ge=0)
    user_id: int = Field(ge=0)
    persons: int = Field(ge=0)
    small_packages: int = Field(ge=0)
    medium_packages: int = Field(ge=0)
    large_Packages: int = Field(ge=0)
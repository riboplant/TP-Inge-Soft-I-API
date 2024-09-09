from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time

""" Schemas with all info """
class Ride(BaseModel):
    ride_id: str# = Field(le=32)
    ubicationFrom: Optional[str] = None#str = Field(min_length=1, max_length=100)
    ubicationTo: Optional[str] = None#str = Field(min_length=1, max_length=100)
    city_from: Optional[str] = None#str = Field(min_length=1, max_length=100)
    city_to: Optional[str] = None#str = Field(min_length=1, max_length=100)
    carPlate: str #= Field(min_length=1, max_length=10)
    driver_id: str #= Field(le=32)
    ride_date: Optional[date] = None#date = Field()
    start_minimum_time:  Optional[time] = None#time = Field()
    start_maximum_time: Optional[time] = None#time = Field()
    real_start_time: Optional[time] = None#time = Field()
    real_end_time: Optional[time] = None#time = Field()

class Carry(BaseModel):
    ride_id: str = Field(le=32)
    user_id: str = Field(le=32)
    persons: int = Field(ge=0)
    small_packages: int = Field(ge=0)
    medium_packages: int = Field(ge=0)
    large_packages: int = Field(ge=0)


class Price(BaseModel):
    ride_id: str = Field(le=32)
    price_person: int = Field(gt=0)
    price_small_package: int = Field(gt=0)
    price_medium_package: int = Field(gt=0)
    price_large_package: int = Field(gt=0)


""" Specific schemas for endpoint purposes """


class RideCreate(BaseModel):
    city_from: Optional[str] = None
    city_to: Optional[str] = None
    ride_date: Optional[date] = None
    start_minimum_time:  Optional[time] = None
    start_maximum_time: Optional[time] = None
    available_space_people: int = Field(gt=0)
    available_space_small_package: int = Field(gt=0)
    available_space_medium_package: int = Field(gt=0)
    available_space_large_package: int = Field(gt=0)

class PriceSet(BaseModel):
    price_person: float = Field(gt=0)
    price_small_package: float = Field(gt=0)
    price_medium_package: float = Field(gt=0)
    price_large_package: float = Field(gt=0)

class searchRideForPackage(BaseModel):
    ubication_from: str = Field(min_length=1, max_length=100)
    ubication_to: str = Field(min_length=1, max_length=100)
    city_from: str = Field(min_length=1, max_length=100)
    city_to: str = Field(min_length=1, max_length=100)
    date: date
    number_small_luggage: int = Field(ge=0)
    number_large_luggage: int = Field(ge=0)
    number_medium_luggage: int = Field(ge=0)



class searchRideForPerson(searchRideForPackage):
    number_people: int = Field(ge=1)


class rideToReturn(BaseModel):
    ride_id: str = Field(le=32)
    city_from: str = Field(min_length=1, max_length=100)
    city_to: str = Field(min_length=1, max_length=100)
    driver_name: str = Field(min_length=1, max_length=100)
    driver_photo: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    date: date

class rideDetailToReturn(rideToReturn):

    available_space_persons: int = Field(ge=0)
    available_space_small_luggage: int = Field(ge=0)
    available_space_medium_luggage: int = Field(ge=0)
    available_space_large_luggage: int = Field(ge=0)
    car_model: str = Field(min_length=1, max_length=50)
    car_plate: str = Field(min_length=1, max_length=10)
    driver_id: str = Field(le=32)
    price_person: int = Field(gt=0)
    price_small_package: int = Field(gt=0)
    price_medium_package: int = Field(gt=0)
    price_large_package: int = Field(gt=0)
    start_maximum_time: time
    start_minimum_time: time
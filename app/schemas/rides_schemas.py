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
    large_Packages: int = Field(ge=0)


class Price(BaseModel):
    ride_id: str = Field(le=32)
    price_person: int = Field(gt=0)
    price_small_package: int = Field(gt=0)
    price_medium_package: int = Field(gt=0)
    price_large_package: int = Field(gt=0)


""" Specific schemas for endpoint purposes """


class RideCreate(BaseModel):
    ubicationFrom: Optional[str] = None
    ubicationTo: Optional[str] = None
    city_from: Optional[str] = None
    city_to: Optional[str] = None
    ride_date: Optional[date] = None
    start_minimum_time:  Optional[time] = None
    start_maximum_time: Optional[time] = None

class PriceSet(BaseModel):
    price_person: int = Field(gt=0)
    price_small_package: int = Field(gt=0)
    price_medium_package: int = Field(gt=0)
    price_large_package: int = Field(gt=0)

class searchRideForPackage(BaseModel):
    ubicationFrom: str = Field(min_length=1, max_length=100)
    ubicationTo: str = Field(min_length=1, max_length=100)
    cityFrom: str = Field(min_length=1, max_length=100)
    cityTo: str = Field(min_length=1, max_length=100)
    date: date
    numberSmallLuggage: int = Field(ge=0)
    numberLargeLuggage: int = Field(ge=0)
    numberMediumLuggage: int = Field(ge=0)



class searchRideForPerson(searchRideForPackage):
    numberPeople: int = Field(ge=1)


class rideToReturn(BaseModel):
    rideId: str = Field(le=32)
    citynFrom: str = Field(min_length=1, max_length=100)
    cityTo: str = Field(min_length=1, max_length=100)
    driver: str = Field(min_length=1, max_length=100)
    driver_photo: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    date: date

class rideDetailToReturn(rideToReturn):

    availableSpacePersons: int = Field(ge=0)
    availableSpaceSmallLuggage: int = Field(ge=0)
    availableSpaceMediumLuggage: int = Field(ge=0)
    availableSpaceLargeLuggage: int = Field(ge=0)
    carModel: str = Field(min_length=1, max_length=50)
    carPlate: str = Field(min_length=1, max_length=10)
    driver_id: str = Field(le=32)
    price_person: int = Field(gt=0)
    price_small_package: int = Field(gt=0)
    price_medium_package: int = Field(gt=0)
    price_large_package: int = Field(gt=0)
    start_maximum_time: time
    start_minimum_time: time
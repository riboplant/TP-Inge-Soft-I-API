from schemas.rides_schemas import searchRideForPackage,searchRideForPerson,rideToReturn,rideDetailToReturn
from datetime import date
from pydantic import Field
from database.connect import engine, SessionLocal
from database.models.model import *
from sqlalchemy import and_


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_people_ride(cityFrom: str, cityTo: str, date: date, persons:  int = Field(ge=0), samllPackages: int = Field(ge=0), mediumPackages: int = Field(ge=0), largePackages: int = Field(ge=0)):

    ridesToRet = []
    index = 0

   # Obtén la sesión y consulta la base de datos
    with next(get_db()) as db_session:
        rides = db_session.query(Rides).filter(
            and_(
                Rides.city_from == cityFrom,
                Rides.city_to == cityTo,
                Rides.date == date    
            )
        )
        for ride in rides:
            driverName = db_session.query(Drivers).filter_by(Drivers.driver_id == ride.driver_id).name
            ridesToRet[index]=rideToReturn(
                ride.ride_id,
                ride.city_from,
                ride.city_to,
                ride.driverName,
                ride.city_from,
                ride.city_from,
                ride.city_from,
                )
    return 0
    
    
    
    # rideToReturn = rideToReturn(
    #     rideId=1,
    #     ubicationFrom=parameteparameters.ubicationFrom,
    #     ubicationTo=parameteparameters.ubicationTo,
    #     driver="Juan",
    #     driver_photo="https://url-to-photo.com/photo.jpg",
    #     price=15000,
    #     date="08/08/2024",
    #     availableSpaceLuggage=5,#tiene que ser al menos la suma de los tres
    #     availableSpacePeople=3
    # )

    # return rideToReturn


def get_package_ride(parameters: searchRideForPackage):
        
    #ver que validaciones hacemos
    #la fecha no puede ser menor a la actual
    #podriamos validar que from y to ambas sean ciudades o si lo hacemos por coordenadas puede ser un radio que el usuario puede elegir


    return 0
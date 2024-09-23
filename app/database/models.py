from sqlalchemy import Boolean, Column, Date, Float, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, Time, text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='users_pk'),
    )

    user_id = Column(String, index=True)
    name = Column(String)
    rider_rating = Column(Float(53))
    email = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean)
    address = Column(String)
    dni = Column(Integer)
    status = Column(String)
    photo = Column(String)

    #drivers = relationship('Drivers', back_populates='user')
    #carrys = relationship('Carrys', back_populates='user')


class Vehicles(Base):
    __tablename__ = 'vehicles'
    __table_args__ = (
        PrimaryKeyConstraint('plate', name='vehicles_pkey'),
    )

    plate = Column(String)
    model = Column(String)
    color = Column(String)
    status = Column(String)

    #driver = relationship('Drivers', secondary='drives', back_populates='vehicles')
    #rides = relationship('Rides', back_populates='vehicles')


class Drivers(Base):
    __tablename__ = 'drivers'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], name='user_id_fk'),
        PrimaryKeyConstraint('driver_id', name='drivers_pkey')
    )

    driver_id = Column(String)
    user_id = Column(String)
    driving_license = Column(Integer)
    driver_rating = Column(Float(53))
    status = Column(String)

    #user = relationship('Users', back_populates='drivers')
    #vehicles = relationship('Vehicles', secondary='drives', back_populates='driver')
    #rides = relationship('Rides', back_populates='driver')


class Drives(Base):
    __tablename__ = 'drives'
    __table_args__ = (
        ForeignKeyConstraint(['driver_id'], ['drivers.driver_id'], name='driver_id_fk'),
        ForeignKeyConstraint(['plate'], ['vehicles.plate'], name='plate_fk'),
        PrimaryKeyConstraint('plate', 'driver_id', name='drivespkey')
    )

    plate = Column(String, nullable=False)
    driver_id = Column(String, nullable=False)

    #driver = relationship('Drivers', back_populates='vehicles')
    #vehicle = relationship('Vehicles', back_populates='driver')


class Rides(Base):
    __tablename__ = 'rides'
    __table_args__ = (
        ForeignKeyConstraint(['car_plate'], ['vehicles.plate'], name='car_plate_fk'),
        ForeignKeyConstraint(['driver_id'], ['drivers.driver_id'], name='driver_id_fk'),
        PrimaryKeyConstraint('ride_id', name='rides_pkey')
    )

    ride_id = Column(String, index=True)
    ubication_from = Column(String)
    ubication_to = Column(String)
    car_plate = Column(String)
    driver_id = Column(String)
    ride_date = Column(Date)
    start_minimum_time = Column(Time(True))
    start_maximum_time = Column(Time(True))
    real_end_time = Column(Time(True))
    real_start_time = Column(Time(True))
    city_from = Column(String)
    city_to = Column(String)
    available_space_people = Column(Integer, server_default=text('0'))
    available_space_small_package = Column(Integer, server_default=text('0'))
    available_space_medium_package = Column(Integer, server_default=text('0'))
    available_space_large_package = Column(Integer, server_default=text('0'))

    #vehicles = relationship('Vehicles', back_populates='rides')
    #driver = relationship('Drivers', back_populates='rides')
    #carrys = relationship('Carrys', back_populates='ride')


class Carrys(Base):
    __tablename__ = 'carrys'
    __table_args__ = (
        ForeignKeyConstraint(['ride_id'], ['rides.ride_id'], name='ride_id_fk'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], name='user_id_fk'),
        PrimaryKeyConstraint('ride_id', 'user_id', name='carry_pkey')
    )

    ride_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    persons = Column(Integer)
    small_packages = Column(Integer)
    medium_packages = Column(Integer)
    large_Packages = Column(Integer)

    #ride = relationship('Rides', back_populates='carrys')
    #user = relationship('Users', back_populates='carrys')


class Prices(Base):
    __tablename__ = 'prices'
    __table_args__ = (
        ForeignKeyConstraint(['ride_id'], ['rides.ride_id'], name='ride_id_fk'),
        PrimaryKeyConstraint('ride_id', name='ride_pkey')
    )

    ride_id = Column(String)
    price_person = Column(Float(53))
    price_small_package = Column(Float(53))
    price_medium_package = Column(Float(53))
    price_large_package = Column(Float(53))

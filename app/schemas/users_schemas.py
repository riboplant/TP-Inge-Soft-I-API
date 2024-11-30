from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time

class User(BaseModel):
    user_id: str = Field()
    name: str = Field(min_length=1)
    rider_rating: Optional[float] = Field(ge=0, le=5)
    email: str = Field(min_length=5, max_length=50)
    disabled: bool = Field()
    address: Optional[str] = Field(min_length=5)
    dni: Optional[int] = Field(ge=0)
    status: Optional[str] = Field()
    photo_url: Optional[str]
    delete_photo_url: Optional[str]

class UserData(BaseModel):
    name: str
    email: str
    address: Optional[str]
    dni: Optional[int]
    photo_url: Optional[str]
    is_driver: Optional[bool]
    user_id: str

class PhotoURLS(BaseModel):
    photo_url: str
    delete_photo_url: str

class Base_64(BaseModel):
    base_64_image: str
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str or None = None


class UserInDB(User):
    hashed_password: str
    rider_rating: Optional[float] = None
    address: Optional[str] = None
    dni: Optional[int] = None
    status: Optional[str] = None
    photo_url: Optional[str] = None
    user_id: str

    # Modelo para la creación de usuarios (contiene la contraseña)
class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: str 
    password: str 
    address: Optional[str]
    dni: int
    photo_url: Optional[str] = None

class Driver(BaseModel):
    user_id: int = Field(ge=0)
    driving_license: int = Field(ge=0)
    driver_rating: float = Field(ge=0, le=5)
    driver_id: int = Field(ge=0)
    status: str = Field()

class Vehicle(BaseModel):
    plate: str = Field()
    model: str = Field()
    color: str = Field()
    


class Drive(BaseModel):
    driver_id: int = Field(ge=0)
    plate: str = Field()


class Comment(BaseModel):
    comment: str = Field()
    rating: int = Field(ge=0, le=5)
    name: str = Field()
    photo_url: Optional[str] = None
    comment_date: Optional[date] = None


class ProfileData(BaseModel):
    name: str = Field()
    email: str = Field()
    photo_url: Optional[str] = None
    avg_rating: int = Field(ge=0, le=5)
    comments: list[Comment] = Field()
    

class UserForListOfRiders(BaseModel):
    user_id: str
    name: str
    photo_url: str
    chat_id: str



""" Specefic schemas for endpoint purposes """


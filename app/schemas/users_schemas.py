from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    user_id: int = Field(ge=0)
    name: str = Field(min_length=1)
    user_rating: Optional[float] = Field(ge=0, le=5)
    email: str = Field(min_length=5, max_length=50)
    disabled: bool = Field()
    address: Optional[str] = Field(min_length=5)
    dni: Optional[int] = Field(ge=0)
    status: Optional[str] = Field()
    photo_id: Optional[int] = Field(ge=0)



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class UserInDB(User):
    hashed_password: str
    user_rating: Optional[float] = None
    address: Optional[str] = None
    dni: Optional[int] = None
    status: Optional[str] = None
    photo_id: Optional[int] = None

    # Modelo para la creación de usuarios (contiene la contraseña)
class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    user_rating: float = Field(ge=0, le=5)
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=8)
    disabled: bool or None = Field(default=None)
    address: Optional[str] = Field(min_length=5)
    dni: int = Field(ge=0)
    status: str = Field()
    photo_id: Optional[int] = Field(ge=0)

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
    status: str = Field()


class Drive(BaseModel):
    driver_id: int = Field(ge=0)
    plate: str = Field()


""" Specefic schemas for endpoint purposes """


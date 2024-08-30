from pydantic import BaseModel, Field
from typing import Optional




class User(BaseModel):
    name: str = Field(min_length=1)
    rating: float = Field(get=0, let=5)
    email: str = Field(min_length=5, max_length=50)
    disabled: bool or None = None

class Ride(BaseModel):
    ubicationFrom: str = Field(min_length=1, max_length=100)
    ubicationTo: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    carModel: str = Field(min_length=1, max_length=50)
    carPlate: str = Field(min_length=1, max_length=10)
    price: float = Field(gt=0)


# Desde aca son cosas para OAUTH de users
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class UserInDB(User):
    hashed_password: str

    # Modelo para la creación de usuarios (contiene la contraseña)
class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    rating: float = Field(ge=0, le=5)
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=8)
    disabled: bool or None = None
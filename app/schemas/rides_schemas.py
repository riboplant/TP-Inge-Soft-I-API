from pydantic import BaseModel, Field
from typing import Optional

class Ride(BaseModel):
    ubicationFrom: str = Field(min_length=1, max_length=100)
    ubicationTo: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    carModel: str = Field(min_length=1, max_length=50)
    carPlate: str = Field(min_length=1, max_length=10)
    price: float = Field(gt=0)
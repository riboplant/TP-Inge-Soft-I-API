from fastapi import HTTPException, Depends, APIRouter, Query, Request, Response
from sqlalchemy.orm import Session
from schemas.users_schemas import Base_64, User, Vehicle
from schemas.rides_schemas import PaymentData
from database.connect import get_db
from services.auth import get_current_active_user
from services.payments import sdk, create_payment, get_payment


router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.post("/create")
async def create_payment_for_ride(title:str, price:float):
    link = create_payment(title=title, quantity=1, unit_price=price, metadata="test")
    return {"link" : link}

@router.post("/owl")
async def get_payment_info(request: Request):
    print(request.headers)
    response = await request.json()
    print(response)
    id = int(response["id"])
    #print(str(response["id"]) + "   " + str(response["date_created"]))
    print(id, id.__class__)

    get_payment(id)
    
    return Response(status_code=200)
    # La clave secreta esta en un header, en x-signature-id


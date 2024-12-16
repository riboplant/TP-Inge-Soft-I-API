from fastapi import HTTPException, Depends, APIRouter, Query, Request, Response
from sqlalchemy.orm import Session
from schemas.users_schemas import Base_64, User, Vehicle
from schemas.rides_schemas import PaymentData
from database.connect import get_db
from services.auth import get_current_active_user
from services.payments import sdk, create_payment, get_payment, get_ride_payment
import json


router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.post("/create")
async def create_payment_for_ride(title:str, price:float, ride_id: str, current_user: User = Depends(get_current_active_user) ,db: Session = Depends(get_db)):
    metadata = {
        "ride_id": ride_id,
        "user_id": current_user.user_id
    }
    metadata_str = json.dumps(metadata)

    return create_payment(title=title, quantity=1, unit_price = (price*0.2), metadata=metadata_str)

@router.post("/owl")
async def get_payment_info(request: Request, db: Session = Depends(get_db)):
    response = await request.json()
    await get_payment(int(response["data"]["id"]), db)
    return Response(status_code=200)
    

@router.post("/get_ride_payment")
async def get_ride_payment_info(ride_id: str, current_user = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_ride_payment(ride_id, current_user, db)
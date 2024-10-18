from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from database.connect import get_db
from config import PaymentSettings
import requests
import mercadopago
from database.models import *
from sqlalchemy.orm import Session
import json

sdk = mercadopago.SDK(PaymentSettings.MP_ACCESS_TOKEN)

def create_preference_data(title:str, quantity:int, unit_price:float, text:str):
    if(quantity <= 0 or unit_price <= 0):
        raise Exception("Illegal arguments for payment creation")
    return {
        "items": [
            {
                "title": title,
                "quantity": quantity,
                "unit_price": unit_price,
            }
        ],
        "metadata": {
            "info": text
        }
    }

def create_payment(title:str, quantity:int, unit_price:float, metadata: str):
    try:
        preference_data = create_preference_data(title=title, quantity=quantity, unit_price=unit_price, text=metadata)
    except Exception as e:
        print("Something went wrong with the payment")
        return None
    

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    link = preference["init_point"]
    # Esto es una url de mp a la que mandamos al usuario
    return {"link" : f"{link}"}

def get_payment(id: int, db: Session):
    
    request = sdk.payment().get(id)


    if request["status"] != 200:
        print("La solicitud falló con el código de estado " + str(request["status"]))
        return 
    
    response = request["response"] # Aca  esta toda la info

 
    if response["status"] != "approved":
        print("Payment not approved yet")
        return
    
    metadataJson = json.loads(response["metadata"]["info"])
    
    carry = db.query(Carrys).filter(Carrys.user_id == metadataJson.user_id, Carrys.ride_id == metadataJson.ride_id).first()

    if carry == None: #esto me hace ruido pero lo valido por las dudas
        return HTTPException(status_code=404, detail="No ride found")

    if carry.payment_id != None:
        return HTTPException(status_code=400, detail="Payment already processed")
    
    
        
    payment_info = Payments(
        payment_id = str(id),
        amount = float(response["transaction_amount"]),
        status = response["status"],
        currency = response["currency_id"],
        time = response["date_created"]
    )

    try:
        if(response["status"] == "approved"):
            setattr(carry, "payment_id", str(id))
        
        db.add(payment_info)
        db.commit()
    except:
        return HTTPException(status_code=500, detail="Error adding the payment")
  

    return JSONResponse(status_code=200, content={"message": "Successfully added the payment"})

def get_ride_payment(ride_id: str, db: Session):
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    if ride == None:
        return {"Error": "Not ride with that id"}
    
    payment = db.query(Payments).filter(Payments.ride_id == ride_id).first()
    if payment == None:
        return {"Error": "Not payment for thay ride"}
    
    return {"payment_id": f"{payment.payment_id}"}
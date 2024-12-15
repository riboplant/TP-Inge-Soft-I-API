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

def create_preference_data(title:str, quantity:int, unit_price:float, text:json):
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

def create_payment(title:str, quantity:int, unit_price:float, metadata:json):
    try:
        preference_data = create_preference_data(title=title, quantity=quantity, unit_price=unit_price, text=metadata)
    except Exception as e:
        print("Something went wrong with the payment")
        raise Exception(e)

    
    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        link = preference["init_point"]
    except Exception as e:
        print("Something went wrong with the payment")
        raise Exception(e)
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
    

    
    metadata = response["metadata"]["info"]
    metadata_dict = json.loads(metadata)

    carry = db.query(Carrys).filter(Carrys.user_id == metadata_dict["user_id"], Carrys.ride_id == metadata_dict["ride_id"]).first()

    # if carry == None: #esto me hace ruido pero lo valido por las dudas
    #     return HTTPException(status_code=404, detail="No ride found")

    # if carry.payment_id != None:
    #     return HTTPException(status_code=400, detail="Payment already processed")
    
    
        
    payment_info = Payments(
        payment_id = str(id),
        amount = float(response["transaction_amount"]),
        status = response["status"],
        currency = response["currency_id"],
        time = response["date_created"]
    )

    try:
        db.add(payment_info)
        db.commit()

        if(response["status"] == "approved"):
            setattr(carry, "payment_id", str(id))

        db.commit()
        
    except:
        return 
  

    return JSONResponse(status_code=200, content={"message": "Successfully added the payment"})

def get_ride_payment(ride_id: str, user_id: str, db: Session):
    ride = db.query(Rides).filter(Rides.ride_id == ride_id).first()
    if ride == None:
        return {"Error": "Not ride with that id"}
    
    carry = db.query(Carrys).filter(Carrys.ride_id == ride_id, Carrys.user_id == user_id).first()
    payment = db.query(Payments).filter(Payments.payment_id == carry.payment_id).first()
    if payment == None:
        raise Exception("Not payment for thay ride")
    
    return {"payment_id": f"{payment.payment_id}"}
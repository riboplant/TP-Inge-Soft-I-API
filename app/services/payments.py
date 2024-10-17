from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from database.connect import get_db
from config import PaymentSettings
import requests
import mercadopago
from database.models import Payments
from sqlalchemy.orm import Session

sdk = mercadopago.SDK(PaymentSettings.MP_ACCESS_TOKEN)

def create_preference_data(title:str, quantity:int, unit_price:float, text: str):
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
    # Esto es una url de mp a la que mandamos al usuario
    return preference["init_point"]

def get_payment(id: int, db: Session):
    
    request = sdk.payment().get(id)

    print(request)

    if request["status"] != 200:
        print("La solicitud falló con el código de estado " + str(request["status"]))
        return 
    
    response = request["response"] # Aca  esta toda la info

 
    if response["status"] != "approved":
        print("Payment not approved yet")
        return
        
    payment_info = Payments(
        ride_id = response["metadata"]["info"],
        payment_id = str(id),
        amount = float(response["transaction_amount"]),
        status = response["status"],
        currency = response["currency_id"],
        time = response["date_created"]
    )
    for i in range(3) :
        print("")
    print(payment_info.__dict__)

    try:
        db.add(payment_info)
        db.commit()
    except:
        return HTTPException(status_code=500, detail="Error adding the payment")
  

    return JSONResponse(status_code=200, content={"message": "Successfully added the payment"})


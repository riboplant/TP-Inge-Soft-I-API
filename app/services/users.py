import os
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from schemas.users_schemas import *
from database.models import *
from database.connect import get_db
from services.auth import get_current_active_user
from uuid import uuid4
from utils.imgBBAPI import *
from fastapi.responses import JSONResponse


async def get_user_data(current_user, db):
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()
    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    
    user = UserData(
        name=user_model.name,
        email=user_model.email,
        address=user_model.address,
        dni=user_model.dni,
        photo_url=user_model.photo_url
    )

    return user


async def edit_photo(base64Image: str, current_user, db):
    
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    
    try:
        img = await upload_image(base64Image)
        
    except:
        
        raise HTTPException(
            status_code=500,
            detail="Error uploading image"
        )
    try:
        setattr(user_model, "photo_url", img["photo_url"])
        setattr(user_model, "delete_photo_url", img["delete_photo_url"])

        db.commit()
        db.refresh(user_model)
        
        
    except:
        raise HTTPException(
            status_code=500,
            detail="Error updating image in db"
        )
   
    return {"photo_url":img["photo_url"]}



def delete_photo(current_user, db):
    try:
        user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()
        setattr(user_model, "photo_url", None)
        setattr(user_model, "delete_photo_url", None)
        db.commit()
        db.refresh(user_model)
    except:
        raise HTTPException(
            status_code=500,
            detail="Error deleting image"
        )
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Image deleted successfully"})
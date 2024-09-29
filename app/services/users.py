import os
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.users_schemas import *
from database.models import *
from database.connect import get_db
from services.auth import get_current_active_user
from uuid import uuid4
from utils.imgBBAPI import *


async def edit_photo(base64Image: str, current_user, db):
    
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    
    if(user_model.photo_url):
        delete_photo(user_model.photo_url)

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



async def delete_photo(base64Image: str, current_user, db):
    
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    
    # if(user_model.photo_url):
    #    delete_image(user_model.photo_url)

    return 0
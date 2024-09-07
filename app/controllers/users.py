from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from schemas.users_schemas import *
from database.models import *
from database.connect import get_db
from services.auth import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)



@router.get("/users/me/")
async def get_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(Users).filter(Users.user_id == current_user.user_id).first()

@router.get("/{user_id}") #esto me permite ver el perfil de otro usuario con datos y resenas correspondientes, debo estar loguado
async def get_user(user_id : int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    response = db.query(Users).filter(Users.user_id == user_id).first()
    if response is None:
        return [{"Usuario": "Usuario con id = {user_id} no exits"}]
    else:
        return response
    
@router.put("/edit")#tenes que estar logueado permite editar el perfil del current
async def edit_user(new_user: User, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_model = db.query(Users).filter(Users.user_id == current_user.user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {current_user.user_id} : Does not exist"
        )
    
    user_model.name = new_user.name
    user_model.email = new_user.email
    user_model.address = new_user.address
    user_model.photo_id = new_user.photo_id

    db.add(user_model)
    db.commit()

    current_user.name = new_user.name
    current_user = await get_current_active_user(current_user)

    return current_user

@router.get("/mycars")# Chequear que sea driver
async def get_user_cars(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return ""


@router.post("/addcar")# Chequear que sea driver
async def add_user_car(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return ""



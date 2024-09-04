from fastapi import HTTPException, Depends, status, APIRouter
from app.schemas.users_schemas import User, UserCreate, UserInDB, Token, TokenData
from app.database.models import users_models, rides_models
from app.database.connect import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from app.services.auth_controller import get_current_active_user
import sys

sys.path.append('..')

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
#registro
#login


@router.get("/users/me/")
async def get_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(users_models.Users).filter(users_models.Users.user_id == current_user.user_id).first()

@router.get("/{user_id}") #esto me permite ver el perfil de otro usuario con datos y resenas correspondientes, debo estar loguado
async def get_user(user_id : int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    response = db.query(users_models.Users).filter(users_models.Users.user_id == user_id).first()
    if response is None:
        return [{"Usuario": "Usuario con id = {user_id} no exits"}]
    else:
        return response
    
@router.put("/edit")#tenes que estar logueado permite editar el perfil del current
async def edit_user(new_user: User, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_model = db.query(users_models.Users).filter(users_models.Users.user_id == current_user.user_id).first()

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



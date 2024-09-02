from fastapi import HTTPException, Depends, status, APIRouter
from schemas.users_schemas import User, UserCreate, UserInDB, Token, TokenData
import database.models.users_models as models
from database.connect import engine, SessionLocal
from sqlalchemy.orm import Session
from auth import get_current_active_user
import sys

sys.path.append('..')

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)
#registro
#login


@router.get("/users/me/") #Tenes que estar logueado
async def get_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == current_user.id).first()

@router.get("/{user_id}") #esto me permite ver el perfil de otro usuario con datos y resenas correspondientes, debo estar loguado
async def get_user(user_id : str):
    return [{"Usuario": "Usuario con id = {id} no exits"}]

@router.put("/edit")#tenes que estar logueado permite editar el perfil del current
async def edit_user():
    return ""
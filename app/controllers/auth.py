from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from schemas.users_schemas import User, UserCreate, Token
from database.models import Users
from database.connect import get_db
from config import AuthSettings as settings
from services.auth import get_current_active_user, create_access_token, authenticate_user, get_password_hash


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        
        user_model = Users()
        
        user_model.user_id = str(uuid4())
        user_model.name = user.name
        user_model.email = user.email
        hashed_password = get_password_hash(user.password)
        user_model.hashed_password = hashed_password
        user_model.disabled = False
        user_model.address = user.address
        user_model.dni = int(user.dni)
        user_model.verified = False
        user_model.photo_url = user.photo_url

        db.add(user_model)
        db.commit()
        db.refresh(user_model)
        
        return {"user_id": user_model.user_id}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

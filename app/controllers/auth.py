from datetime import timedelta
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from schemas.users_schemas import User, UserInDB, UserCreate, Token, TokenData
import database.models.users_models as models
from database.connect import engine
from config import AuthSettings as settings
from services.auth_controller import get_db, get_current_active_user, create_access_token, authenticate_user, get_password_hash
import sys
sys.path.append('..')



models.Base.metadata.create_all(bind=engine)


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
        data={"sub": user.name}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user_model = models.Users()
    user_model.name = user.name
    user_model.user_id = user.user_rating
    user_model.email = user.email
    user_model.disabled = False

    # Hashear la contraseña antes de almacenarla
    hashed_password = get_password_hash(user.password)
    user_model.hashed_password = hashed_password

    db.add(user_model)
    db.commit()
    db.refresh(user_model)    
    return {"msg": "User registered successfully"} 
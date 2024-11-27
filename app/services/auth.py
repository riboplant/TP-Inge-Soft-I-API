from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status, WebSocket
from sqlalchemy.orm import Session


from schemas.users_schemas import UserInDB, TokenData
from database.connect import get_db 
from database.models import *
from config import AuthSettings as settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    user_data = db.query(Users).filter(Users.email == email).first()
    if not user_data:
        user_data = db.query(Users).filter(Users.user_id == email).first()
    if user_data:
        return UserInDB(**user_data.__dict__)
    return None

def authenticate_user( db: Session = Depends(get_db), email: str = None, password: str = None):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.key, algorithms=[settings.algorithm])
        id: str = payload.get("sub")
        if id is None:
            raise credential_exception
        token_data = TokenData(id=id)
    except JWTError:

        raise credential_exception
    
    user = get_user(db, email=token_data.id)
    if user is None:
        raise credential_exception

    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


async def get_current_user_from_ws(websocket: WebSocket, db):
    token = websocket.headers.get("Authorization")  
    
    if not token:
        raise HTTPException(status_code=400, detail="Authorization token missing")
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, settings.key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = get_user(db, email=user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
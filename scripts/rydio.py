from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class User(BaseModel):
    name: str = Field(min_length=1)
    rating: float = Field(get=0, let=5)
    email: str = Field(min_length=5, max_length=50)
    disabled: bool or None = None

class Ride(BaseModel):
    ubicationFrom: str = Field(min_length=1, max_length=100)
    ubicationTo: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    carModel: str = Field(min_length=1, max_length=50)
    carPlate: str = Field(min_length=1, max_length=10)
    price: float = Field(gt=0)


# Desde aca son cosas para OAUTH de users
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hasta aca, es set up

app = FastAPI()

# Desde aca son funciones auxiliares para el OAUTH de usuarios

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session = Depends(get_db), username: str = None):
    user_data = db.query(models.Users).filter(models.Users.name == username).first()
    return UserInDB(**user_data)

def authenticate_user(db: Session = Depends(get_db), username: str = None, password: str = None):
    user = get_user(db, username)
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
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(get_db, username=token_data.username)
    if user is None:
        raise credential_exception

    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

# Hasta aca

# A partir de aca son metodos para el OAUTH de usuarios

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(get_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items")
async def read_own_atributes(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]

# Hasta aca

@app.get("/rides")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Rides).all()


@app.post("/rides")
def create_ride(ride: Ride, db: Session = Depends(get_db)):
    ride_model = models.Rides()
    ride_model.ubication_from = ride.ubicationFrom
    ride_model.ubication_to = ride.ubicationTo
    ride_model.description = ride.description
    ride_model.car_model = ride.carModel
    ride_model.car_plate = ride.carPlate
    ride_model.price = ride.price

    db.add(ride_model)
    db.commit()


@app.delete("/rides")
def delete_ride(ride_id: int, db: Session = Depends(get_db)):

    ride_model = db.query(models.Rides).filter(models.Rides.id == ride_id).first()

    if ride_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {ride_id} : Does not exist"
        )
    
    db.query(models.Rides).filter(models.Rides.id == ride_id).delete()
    db.commit()


@app.post("/users/register")
def register_user(user: User, db: Session = Depends(get_db)):
    user_model = models.Users()
    user_model.name = user.name
    user_model.rating = user.rating

    db.add(user_model)
    db.commit()

@app.put("/users")
def edit_user(user_id: int, user:User, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} : Does not exist"
        )
    
    user_model.name = user.name
    user_model.rating = user.rating

    db.add(user_model)
    db.commit()

    return user
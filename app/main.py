from fastapi import FastAPI
from app.controllers import rides, users
from controllers import auth, admin

app = FastAPI()


app.include_router(rides.router)
app.include_router(users.router, tags=["users"])
app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"])

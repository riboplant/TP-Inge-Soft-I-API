from fastapi import FastAPI
from app.routers import rides_router, users_router, main_router


app = FastAPI()


app.include_router(main_router.router)
app.include_router(rides_router.router)
app.include_router(users_router.router)
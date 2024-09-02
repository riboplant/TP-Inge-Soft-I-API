from fastapi import FastAPI
#from app.routers import rides_router, users_router, auth, admin
from routers import auth, admin

app = FastAPI()


#app.include_router(main_router.router)
#app.include_router(rides_router.router)
#app.include_router(users_router.router)
app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"])
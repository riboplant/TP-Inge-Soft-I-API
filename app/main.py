from fastapi import FastAPI
from app.controllers import rides_router
#from app.controllers import auth, admin, users_router
from app.database.insertDataInDB import insertData
app = FastAPI()


#app.include_router(main_router.router)
app.include_router(rides_router.router)
# app.include_router(users_router.router, tags=["users"])
# app.include_router(auth.router, tags=["auth"])
# app.include_router(admin.router, tags=["admin"])
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import rides, users, auth, admin, payments, chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)


app.include_router(rides.router)
app.include_router(users.router, tags=["users"])
app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"])
app.include_router(payments.router, tags=["payments"])
app.include_router(chat.router, tags=["chat"])


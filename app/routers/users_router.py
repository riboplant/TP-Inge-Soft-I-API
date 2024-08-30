from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


#registro
#login


@router.get("/users/me/") #Tenes que estar logueado
async def get_me():
    return "bla"

@router.get("/{user_id}") #esto me permite ver el perfil de otro usuario con datos y resenas correspondientes, debo estar loguado
async def get_user(user_id : str):
    return [{"Usuario": "Usuario con id = {id} no exits"}]

@router.put("/edit")#tenes que estar logueado permite editar el perfil del current
async def edit_user():
    return ""
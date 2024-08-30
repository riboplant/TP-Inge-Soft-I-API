from fastapi import APIRouter


router = APIRouter(
    prefix="/rides",
    tags=["rides"],
)


#esto es para buscar viajes para personas
@router.get("/people")
async def get_people_ride(location_from: str, location_to:str , date:str ):
    return [{"Viajes": "No se encontro ninguno"}] #llamar a una funcion que este en controller que busque viajese que macheen con esta busqueda o algo parecido

#esto es para buscar viajes para paquetes
@router.get("/package")
async def get_package_ride(location_from: str, location_to:str , date:str ):
    return [{"Viajes": "No se encontro ninguno"}] #llamar a una funcion que este en controller que busque viajese que macheen con esta busqueda o algo parecido


@router.post("/create")#tiene que estar logueado
async def create_ride():#quien es el driver, ver manejo de sesiones.El driver es el usuario logueado en ese momento
    return "Vemos que retorna, puede ser un codigo nomas y listo"#creo que hay que definir un schema para Ride

#esto sirve para que el formulario de edicion de un viaje nos pida todos los datos y despues los edite y nos llamen al edit_ride
@router.get("/ride{ride_id}") #tiene que estar logueado y el viaje debe ser suyo
async def get_ride(ride_id : int):
    return ""

@router.put("/edit/{ride_id}")#tiene que estar logueado y el viaje debe ser suyo
async def edit_ride(ride_id : int):#si ya te pasaste de la fecha te decimos que no podes editar
    return "Vemos que retorna, puede ser un codigo nomas y listo"#creo que hay que definir un schema para Ride

@router.delete("/delete/{ride_id}")#tiene que estar logueado y el viaje debe ser suyo
async def edit_ride(ride_id : int): # si ya te pasaste de la fecha te decimos que no podes borrar
        return "Lo borre/no lo borre"

@router.get("/history")#Los viajes tales que su fecha es menor a la actual. Tiene que estar logueado para acceder
async def my_rides_history():
     return ""

@router.get("/upcoming")#Los viajes tales que su fecha es mayor a la actual. Tiene que estar logueado para acceder
async def my_rides_history():
     return ""
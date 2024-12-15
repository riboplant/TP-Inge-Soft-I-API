import requests
from collections import defaultdict

class db_settings():
    user: str = "avnadmin"
    password: str = "AVNS_Jjvv_4zuzfe561yPPTV"
    host: str = "sql-db-inge-soft-tp.l.aivencloud.com"
    port: int = 14430
    name: str = "defaultdb"

DBSettings = db_settings()

class auth_settings():
    key: str = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    
AuthSettings = auth_settings()

class payment_settings():
    MP_ACCESS_TOKEN = "APP_USR-698825110753956-121416-a4d4647b9e65ed3ab37d32b5e5299088-237579851"
    
PaymentSettings = payment_settings()


response = requests.get(url="http://datos.energia.gob.ar/api/3/action/package_show?id=precios-en-surtidor")
if(response.status_code == 200):
    id = response.json()["result"]["resources"][0]["id"] # 0 es para vigentes, 1 para anteriores y 2 para apps mobile

response = requests.get(url=f"http://datos.energia.gob.ar/api/3/action/datastore_search?resource_id={id}")
if response.status_code == 200:
    data = response.json()["result"]["records"]

precios_combustible = defaultdict(list)
for item in data:
    producto = item["producto"]
    precio = item['precio']
    precios_combustible[producto].append(precio)

promedios = {}
for producto, precios in precios_combustible.items():
    promedio = sum(precios) / len(precios)
    promedios[producto] = promedio

# for producto, promedio in promedios.items():
#     print(f"Promedio de {producto}: {promedio:.2f}")

PRECIO_NAFTA_PROMEDIO = promedios.get('Nafta (premium) de más de 95 Ron')
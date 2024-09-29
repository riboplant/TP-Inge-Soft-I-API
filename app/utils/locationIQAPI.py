import requests
from dotenv import load_dotenv
from decouple import config

load_dotenv()
API_KEY = str(config('API_KEY_LOCATIONIQ'))    
    
    
    
def get_coordinates(city):
    url = f'https://us1.locationiq.com/v1/search.php?key={API_KEY}&q={city}&format=json'
    response = requests.get(url)
    data = response.json()
    if 'error' in data:
            raise Exception("Cannot found {city} cordinates")
    return float(data[0]['lat']), float(data[0]['lon'])

def _calculate_distance(lon1, lat1, lon2, lat2):
    url = f'https://us1.locationiq.com/v1/directions/driving/{lon1},{lat1};{lon2},{lat2}?key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    
    if 'routes' in data:
        
        routes = data['routes']
        if routes:
            route = routes[0]
            if 'legs' in route:
                legs = route['legs']
                if legs:
                    leg = legs[0]
                    return leg['distance']/1000
    return None




def get_distance_between(city_from, city_to):   
    try:
        lat_city_from, lon_city_from = get_coordinates(city_from)
        lat_city_to, lon_city_to = get_coordinates(city_to)
    except:
        raise

    distance_km = _calculate_distance(lon_city_from, lat_city_from, lon_city_to, lat_city_to)

    if distance_km == None:
        raise Exception("Cannto calculate the distance between {city_from} and {city_to}")
        return -1

    return distance_km



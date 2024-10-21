import httpx  
from dotenv import load_dotenv
from decouple import config
from fastapi import HTTPException

load_dotenv()
NOTIFICATION_APP_ID = str(config('NOTIFICATION_APP_ID'))
NOTIFICATION_APP_KEY = str(config('NOTIFICATION_APP_KEY'))

async def send_notification(user_id, title, message):
    url = 'https://app.nativenotify.com/api/indie/notification'
    payload = {
        'subID': user_id,
        'appId': NOTIFICATION_APP_ID,
        'appToken': NOTIFICATION_APP_KEY,
        'title': title,
        'message': message
    }
    
    async with httpx.AsyncClient() as client:  
        response = await client.post(url, json=payload, timeout=10000)
    
    if response.status_code < 200 or response.status_code >= 300:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return 0

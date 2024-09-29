import httpx  
from dotenv import load_dotenv
from decouple import config
from fastapi import HTTPException

load_dotenv()
API_KEY = str(config('API_KEY_IMGBB'))

async def upload_image(base64Image: str):
    try:
        
        body = {
            'image': base64Image
        }

        async with httpx.AsyncClient() as client:  
            response = await client.post(
                f"https://api.imgbb.com/1/upload?expiration=600&key={API_KEY}",
                data=body,
                timeout=10000
            )

        
        if response.status_code == 200:
            result = response.json()  
          
            return {
                "photo_url" : result['data']['url'], 
                "delete_photo_url": result['data']['delete_url']
            }
        else:
            
            raise HTTPException(
                status_code=response.status_code,
                detail="Error uploading image"
            )

    except Exception as e:
       
        raise HTTPException(
            status_code=500,
            detail="Error uploading image"
        )

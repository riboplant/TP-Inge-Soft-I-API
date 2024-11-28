from fastapi import APIRouter, WebSocket, HTTPException, Depends
from database.connect import get_db 
from sqlalchemy.orm import Session
from datetime import date

from services.chat import chat, get_messages
from services.auth import get_user_by_token
from controllers.auth import get_current_active_user

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.get("/messages/{chat_id}")
def messages(chat_id: str, limit: int = 20, before: str = None, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    ans = get_messages(chat_id, limit, current_user, db, before)
    print(ans)
    return ans

@router.websocket("/{chat_id}")
async def chat_ws(websocket: WebSocket, chat_id: str, token: str, db: Session = Depends(get_db)):
    if not token:
        await websocket.close()
    user = await get_user_by_token(token, db)

    if not user:
        await websocket.close()
        raise HTTPException(status_code=401, detail="User not found")

    return await chat(chat_id, user, websocket, db)
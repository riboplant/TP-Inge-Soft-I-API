from fastapi import APIRouter, WebSocket, HTTPException, Depends
from database.connect import get_db 
from sqlalchemy.orm import Session

from services.chat import chat, get_messages
from services.auth import get_user_by_token

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.get("/chats/{chat_id}/messages")
def messages(chat_id: str, limit: int = 20, before: str = None, db: Session = Depends(get_db)):
    return get_messages(chat_id, limit, before, db)

@router.websocket("/{chat_id}")
async def chat_ws(websocket: WebSocket, chat_id: str, token: str, db: Session = Depends(get_db)):
    if not token:
        await websocket.close()
    user = await get_user_by_token(token, db)

    if not user:
        await websocket.close()
        raise HTTPException(status_code=401, detail="User not found")

    return await chat(chat_id, user, websocket, db)
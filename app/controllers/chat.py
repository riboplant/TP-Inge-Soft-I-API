from fastapi import APIRouter, WebSocket, HTTPException, Depends
from database.connect import get_db 
from sqlalchemy.orm import Session
from datetime import date

from services.chat import *
from services.auth import get_user_by_token
from controllers.auth import get_current_active_user

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.get("/messages/{chat_id}")
def messages_get(chat_id: str, limit: int = 20, before: str = None, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return get_messages(chat_id, limit, current_user, db, before)

@router.put("/message/{message_id}")
async def update_message(message_id: str, new_message: str, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return await message_update(message_id, new_message, db, current_user)

@router.delete("/message/{message_id}")
async def delete_message(message_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return await message_delete(message_id, db, current_user)

@router.get("/other_user/{chat_id}")
def other_user(chat_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return get_other_user(chat_id, current_user, db)

@router.post("/create")
async def chat_create(driver_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return await create_chat(driver_id, current_user.user_id, db)

@router.get("/list")
async def chat_list(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return get_chats(current_user, db)

@router.websocket("/{chat_id}")
async def chat_ws(websocket: WebSocket, chat_id: str, token: str, db: Session = Depends(get_db)):
    if not token:
        await websocket.close()
    user = await get_user_by_token(token, db)

    if not user:
        await websocket.close()
        raise HTTPException(status_code=401, detail="User not found")

    return await chat(chat_id, user, websocket, db)
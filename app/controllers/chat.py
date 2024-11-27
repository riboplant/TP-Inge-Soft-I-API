from fastapi import APIRouter, WebSocket

from services.chat import *

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.websocket("/{chat_id}")
async def chat_ws(websocket: WebSocket, chat_id: str, db: Session = Depends(get_db)):
    return await chat(chat_id, websocket, db)
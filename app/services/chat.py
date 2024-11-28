from fastapi import Depends, APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, HTTPException
from pytz import timezone
from sqlalchemy.orm import Session
from datetime import datetime

from services.auth import get_current_user_from_ws
from schemas.rides_schemas import *
from schemas.users_schemas import User
from database.models import *
from database.connect import get_db
from uuid import uuid4




class ConnectionManager:
    """Class defining socket events"""
    def __init__(self):
        """init method, keeping track of connections"""
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket, chat_id: str):
        """connect event"""
        await websocket.accept()
        self.active_connections.append({websocket, chat_id})

    async def send_message(self, message: str, websocket: WebSocket, current_user, chat_id, db: Session):
        """Direct Message"""
        
        buenos_aires_tz = timezone('America/Argentina/Buenos_Aires')
        current_time = datetime.now(buenos_aires_tz)
        
        new_message = Message(
            msg_id=str(uuid4()),
            msg=message,
            writer_id=current_user.user_id,
            chat_id=chat_id,
            sent_at=current_time
        )

        try:
            db.add(new_message)
            db.commit()
        except Exception as e:
            db.rollback()
            raise WebSocketException(status_code=500, detail="Internal Server Error")

        await websocket.send_json({
            "action": "new_message",
            "message": message,
            "sent_at": current_time.isoformat(),
            "writer_id": current_user.user_id
        })

    async def send_message_update(self, chat_id: str, message_id: str, new_msg: str):
        for connection, chat in self.active_connections:
            if chat == chat_id:
                await connection.send_json({
                    "action": "edit_message",
                    "message_id": message_id,
                    "new_msg": new_msg
                })
                
    async def send_message_remove(self, chat_id: str, message_id: str):
        for connection, chat in self.active_connections:
            if chat == chat_id:
                await connection.send_json({
                    "action": "remove_message",
                    "message_id": message_id,
                })
    
    def disconnect(self, websocket: WebSocket):
        """disconnect event"""
        for connection in self.active_connections:
            if websocket in connection:
                self.active_connections.remove(connection)
                break



manager = ConnectionManager()



async def chat(chat_id: str, user: User, websocket: WebSocket, db):
    
    
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if not chat:
        raise WebSocketException(404, "Chat not found")
    
    if user.user_id not in [chat.user1_id, chat.user2_id]:
        raise WebSocketException(403, "Forbidden")

    await manager.connect(websocket, chat_id)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "":
                continue
            await manager.send_message(data, websocket, user, chat_id, db)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def get_messages(chat_id: str, limit: int, current_user, db: Session, before: str):

    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if current_user.user_id not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = db.query(Message).filter(Message.chat_id == chat_id)

    if before:
        try:
            before_datetime = datetime.strptime(before, "%Y-%m-%dT%H:%M:%S%z")  # Acepta la Z como zona horaria UTC
            query = query.filter(Message.sent_at < before_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'before' timestamp format")

    messages = query.order_by(Message.sent_at.desc()).limit(limit).all()

    return {"messages": messages}

def message_delete(message_id: str, db: Session, current_user):
    message = db.query(Message).filter(Message.msg_id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.writer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    manager.send_message_remove(message.chat_id, message_id)
    
    db.delete(message)
    db.commit()

    return {"message": "Message deleted"}

def message_update(message_id: str, new_message: str, db: Session, current_user):
    message = db.query(Message).filter(Message.msg_id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.writer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    message.msg = new_message
    db.commit()

    manager.send_message_update(message.chat_id, message_id, new_message)

    return {"message": "Message updated"}
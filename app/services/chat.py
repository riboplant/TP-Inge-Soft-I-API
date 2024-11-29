from fastapi import Depends, APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, HTTPException
from pytz import timezone
from sqlalchemy.orm import Session
from datetime import datetime

from schemas.rides_schemas import *
from database.models import *
from uuid import uuid4
from schemas.users_schemas import User

class ConnectionItems:
    def __init__(self, websocket: WebSocket, chat_id: str):
        self.websocket = websocket
        self.chat_id = chat_id

def _add_message(message: str, current_user, chat_id, db: Session):        
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

    return new_message

class ConnectionManager:
    """Class defining socket events"""
    def __init__(self):
        """init method, keeping track of connections"""
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket, chat_id: str):
        """connect event"""
        await websocket.accept()
        self.active_connections.append(ConnectionItems(websocket, chat_id))

    async def send_message(self,websocket: WebSocket, new_message):
        """Direct Message"""
        await websocket.send_json(
        {
            "msg_id": new_message.msg_id,
            "msg": new_message.msg,
            "writer_id": new_message.writer_id,
            "chat_id": new_message.chat_id,
            "sent_at": new_message.sent_at.isoformat(),
            "action": "new_message"
        })

    async def send_message_update(self, chat_id: str, message_id: str, new_msg: str):
        for connection in self.active_connections:
            if connection.chat_id == chat_id:
                await connection.websocket.send_json({
                    "action": "edit_message",
                    "message_id": message_id,
                    "new_msg": new_msg
                })
                
    async def send_message_remove(self, chat_id: str, message_id: str):
        for connection in self.active_connections:
            if connection.chat_id == chat_id:
                await connection.websocket.send_json({
                    "action": "remove_message",
                    "message_id": message_id,
                })
    
    def disconnect(self, websocket: WebSocket):
        """disconnect event"""
        for connection in self.active_connections:
            if websocket == connection.websocket:
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
            new_message = _add_message(data, user, chat_id, db)
            print(manager.active_connections)
            for connection in manager.active_connections:
                if connection.chat_id == chat_id:
                    await manager.send_message(connection.websocket, new_message)
            
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

    return messages

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

def get_other_user(chat_id: str, current_user, db: Session):
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if current_user.user_id not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    other_user_id = chat.user1_id if chat.user1_id != current_user.user_id else chat.user2_id

    other_user = db.query(Users).filter(Users.user_id == other_user_id).first()

    return {"user_id": other_user.user_id, "username": other_user.name }
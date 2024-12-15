from fastapi import Depends, APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, HTTPException
from pytz import timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from schemas.rides_schemas import *
from database.models import *
from uuid import uuid4
from schemas.users_schemas import User
from utils.notifications import send_notification

class ConnectionItems:
    def __init__(self, websocket: WebSocket, chat_id: str):
        self.websocket = websocket
        self.chat_id = chat_id

async def _add_message(message: str, current_user, chat_id, db: Session):        
    buenos_aires_tz = timezone('America/Argentina/Buenos_Aires')
    current_time = datetime.now(buenos_aires_tz)
    
    new_message = Message(
        msg_id=str(uuid4()),
        msg=message,
        writer_id=current_user.user_id,
        chat_id=chat_id,
        sent_at=current_time
    )

    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

    other_user_id = chat.user1_id if chat.user1_id != current_user.user_id else chat.user2_id

    await send_notification(other_user_id, current_user.name , message)
    

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
            "edited": new_message.edited,
            "action": "new_message"
        })

    async def send_message_update(self, chat_id: str, message_id: str, new_msg: str):
        """Direct Message"""
        for connection in self.active_connections:
        
            if connection.chat_id == chat_id:
                await connection.websocket.send_json({
                    "action": "edit_message",
                    "msg_id": message_id,
                    "msg": new_msg
                })
                
    async def send_message_remove(self, chat_id: str, message_id: str):
        """Direct Message"""
        for connection in self.active_connections:
            
            if connection.chat_id == chat_id:
                await connection.websocket.send_json({
                    "action": "remove_message",
                    "msg_id": message_id,
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

async def message_delete(message_id: str, db: Session, current_user):
    message = db.query(Message).filter(Message.msg_id == message_id).first()

    buenos_aires_tz = timezone('America/Argentina/Buenos_Aires')
    current_time = datetime.now(buenos_aires_tz)
    time_difference = current_time - message.sent_at

    if time_difference.total_seconds() > 600:
        raise HTTPException(status_code=403, detail="Cannot delete messages older than 10 minutes")

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.writer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    await manager.send_message_remove(message.chat_id, message_id)
    
    try:
        db.delete(message)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Message deleted"}

async def message_update(message_id: str, new_message: str, db: Session, current_user):
    message = db.query(Message).filter(Message.msg_id == message_id).first()

    buenos_aires_tz = timezone('America/Argentina/Buenos_Aires')
    current_time = datetime.now(buenos_aires_tz)
    time_difference = current_time - message.sent_at

    if time_difference.total_seconds() > 600:
        raise HTTPException(status_code=403, detail="Cannot update messages older than 10 minutes")

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.writer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        setattr(message, "msg", new_message)
        setattr(message, "edited", True)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


    await manager.send_message_update(message.chat_id, message_id, new_message)

    return {"message": "Message updated"}

def get_other_user(chat_id: str, current_user, db: Session):
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if current_user.user_id not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    other_user_id = chat.user1_id if chat.user1_id != current_user.user_id else chat.user2_id

    other_user = db.query(Users).filter(Users.user_id == other_user_id).first()

    return {"user_id": other_user.user_id, "username": other_user.name, "photo_url": other_user.photo_url}


def create_chat(driver_id: str, user2_id: str, db: Session):

    user1_id = db.query(Drivers).filter(Drivers.driver_id == driver_id).first().user_id

    chat = db.query(Chat).filter(
            or_(
                (Chat.user1_id == user1_id) & (Chat.user2_id == user2_id),
                (Chat.user2_id == user1_id) & (Chat.user1_id == user2_id)
            )
            ).first()

    if chat:
        return {"chat_id": chat.chat_id}

    chat = Chat(
        chat_id=str(uuid4()),
        user1_id=user1_id,
        user2_id=user2_id
    )

    try:
        db.add(chat)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    return {"chat_id": chat.chat_id}

def get_chats(current_user, db: Session):
    chats = db.query(Chat).filter(or_(Chat.user1_id == current_user.user_id, Chat.user2_id == current_user.user_id)).all()

    chats_with_last_message = []
    buenos_aires_tz = timezone("America/Argentina/Buenos_Aires")
    
    for chat in chats:
        last_message = db.query(Message).filter(Message.chat_id == chat.chat_id).order_by(Message.sent_at.desc()).first()
        chats_with_last_message.append((chat, last_message.sent_at if last_message else datetime.min.replace(tzinfo=buenos_aires_tz)))

    if chats_with_last_message == []:
        return []
    
    chats_with_last_message.sort(key=lambda x: x[1], reverse=True)

    sorted_chats = [chat for chat, _ in chats_with_last_message]
    result = []
    for chat in sorted_chats:
        other_user = get_other_user(chat.chat_id, current_user, db)
        last_message = db.query(Message).filter(Message.chat_id == chat.chat_id).order_by(Message.sent_at.desc()).first()
        result.append({
            "chat_id": chat.chat_id,
            "name_other_user": other_user["username"],
            "photo_url_other_user": other_user["photo_url"],
            "last_msg": last_message.msg if last_message else None,
            "last_msg_time": last_message.sent_at.isoformat() if last_message else None
        })
    return result
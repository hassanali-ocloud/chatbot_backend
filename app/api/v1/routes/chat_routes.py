from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.deps import get_uid, db
from app.schemas.chat import ChatCreateRequest, ChatResponse, ChatListResponse
from app.schemas.message import MessageSendRequest, MessagesListResponse
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/chats", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(payload: ChatCreateRequest, uid: str = Depends(get_uid), database = Depends(db)):
    service = ChatService(database)
    chat = await service.create_chat(uid, payload.title)
    return chat

@router.get("/chats", response_model=ChatListResponse)
async def list_chats(uid: str = Depends(get_uid), database = Depends(db)):
    service = ChatService(database)
    chats = await service.list_chats(uid)
    return {"chats": chats}

@router.get("/chats/{chat_id}/messages", response_model=MessagesListResponse)
async def get_messages(chat_id: str, uid: str = Depends(get_uid), database = Depends(db), order: str = "asc"):
    service = ChatService(database)
    msgs = await service.get_messages(uid, chat_id, order=order)
    return {"messages": msgs}

@router.post("/chats/{chat_id}/messages")
async def send_message(chat_id: str, payload: MessageSendRequest, uid: str = Depends(get_uid), database = Depends(db)):
    service = ChatService(database)
    try:
        res = await service.send_message(uid, chat_id, payload.text, payload.clientMessageId)
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str, uid: str = Depends(get_uid), database = Depends(db)):
    service = ChatService(database)
    status = await service.delete_chat(chat_id)
    if not status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return {"status": "deleted"}

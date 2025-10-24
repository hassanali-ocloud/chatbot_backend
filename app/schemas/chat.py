from pydantic import BaseModel
from typing import Optional, List

class ChatCreateRequest(BaseModel):
    title: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: str
    last_updated: str

class ChatListResponse(BaseModel):
    chats: List[ChatResponse]

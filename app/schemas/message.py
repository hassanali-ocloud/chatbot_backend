from pydantic import BaseModel
from typing import Optional, List

class MessageSendRequest(BaseModel):
    text: str
    clientMessageId: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    user_id: str
    role: str
    text: str
    created_at: str

class MessagesListResponse(BaseModel):
    messages: List[MessageResponse]



from pydantic import BaseModel
from typing import Optional, List

class MessageSendRequest(BaseModel):
    text: str
    clientMessageId: Optional[str] = None

class MessagesListResponse(BaseModel):
    messages: List[dict]

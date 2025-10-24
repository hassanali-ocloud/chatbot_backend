from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class Role(Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"

class MessageModel(BaseModel):
    id: str
    chat_id: str
    content: str
    role: Role
    created_at: datetime
    message_id: str
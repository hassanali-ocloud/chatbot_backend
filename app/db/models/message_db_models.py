from typing import TypedDict, Optional
from datetime import datetime
from enum import Enum

class MessageRole(Enum):
        USER = "user"
        SYSTEM = "system"

class MessageDBModel(TypedDict):
    _id: Optional[str]
    chat_id: str
    user_id: str
    role: MessageRole
    text: str
    created_at: datetime
    client_message_id: Optional[str]
    reply_to: Optional[str]

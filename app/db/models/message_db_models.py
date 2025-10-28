from typing import TypedDict, Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId
from pydantic import BaseModel
from app.config.enums import MessageRole

class MessageDBModel(BaseModel):
    _id: str
    chat_id: str
    user_id: str
    role: MessageRole
    text: str
    created_at: datetime
    client_message_id: Optional[str]

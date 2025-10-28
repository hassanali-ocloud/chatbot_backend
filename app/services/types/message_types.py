from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from app.config.enums import MessageRole

@dataclass
class MessageServiceModel:
    id: str
    chat_id: str
    user_id: str
    role: MessageRole
    text: str
    created_at: datetime
    client_message_id: str | None

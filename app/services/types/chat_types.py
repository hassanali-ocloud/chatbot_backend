from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChatServiceModel:
    id: str
    user_id: str
    title: str
    created_at: datetime
    last_updated: datetime

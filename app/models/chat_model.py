from pydantic import BaseModel
from datetime import datetime

class ChatModel(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    last_updated: datetime

from typing import Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

class ChatDBModel(BaseModel):
    _id: Optional[str] = None
    user_id: str
    title: str
    created_at: datetime
    last_updated: datetime

from typing import Any, Dict, List
from bson import ObjectId
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ChatRepo:
    def __init__(self, db):
        self._col = db.get_collection("chats")

    async def create(self, user_id: str, title: str) -> Dict[str, Any]:
        now = datetime.now()
        doc = {"user_id": user_id, "title": title, "created_at": now, "last_updated": now}
        res = await self._col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    async def list(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self._col.find({"user_id": user_id}).sort("last_updated", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return docs

    async def get(self, user_id: str, chat_id: str):
        _id = ObjectId(chat_id)
        doc = await self._col.find_one({"_id": _id, "user_id": user_id})
        return doc

    async def touch(self, chat_id: str):
        _id = ObjectId(chat_id)
        await self._col.update_one({"_id": _id}, {"$set": {"last_updated": datetime.now()}})

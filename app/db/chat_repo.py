from typing import Any, Dict, List
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.chat_db_models import ChatDBModel
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ChatRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db.get_collection("chats")

    async def create(self, user_id: str, title: str) -> ChatDBModel:
        now = datetime.now()
        doc = ChatDBModel(user_id=user_id, title=title or "New chat", created_at=now, last_updated=now)
        res = await self._col.insert_one(doc.model_dump())
        doc._id = res.inserted_id
        return doc

    async def list(self, user_id: str) -> List[ChatDBModel]:
        cursor = self._col.find({"user_id": user_id}).sort("last_updated", -1)
        docs = await cursor.to_list()
        out: List[ChatDBModel] = []
        for doc in docs:
            chat = ChatDBModel(**doc)
            chat._id = str(doc["_id"])
            out.append(chat)
        return out

    async def get(self, user_id: str, chat_id: str) -> ChatDBModel | None:
        _id = ObjectId(chat_id)
        doc = await self._col.find_one({"_id": _id, "user_id": user_id})
        if doc:
            return ChatDBModel(**doc)
        return None

    async def update(self, chat_id: str):
        _id = ObjectId(chat_id)
        await self._col.update_one({"_id": _id}, {"$set": {"last_updated": datetime.now()}})

    async def delete(self, chat_id: str) -> bool:
        result = await self._col.delete_one({"_id": ObjectId(chat_id)})
        return result.deleted_count > 0

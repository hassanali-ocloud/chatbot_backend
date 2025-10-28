from typing import Any, Dict, List
from datetime import datetime
from bson import ObjectId
from app.services.types.message_types import MessageRole
from app.utils.logger import get_logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.message_db_models import MessageDBModel

logger = get_logger(__name__)

class MessageRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db.get_collection("messages")

    async def create(self, chat_id: str, user_id: str, role: MessageRole, text: str, client_message_id: str | None = None) -> MessageDBModel:
        now = datetime.now()
        doc = MessageDBModel(
            chat_id=chat_id,
            user_id=user_id,
            role=role,
            text=text,
            created_at=now,
            client_message_id=client_message_id or None
        )
        res = await self._col.insert_one(doc.model_dump())
        doc._id = res.inserted_id
        return doc

    async def list(self, chat_id: str, order: str = "asc") -> List[MessageDBModel]:
        sort_dir = 1 if order == "asc" else -1
        cursor = self._col.find({"chat_id": chat_id}).sort("created_at", sort_dir)
        docs = await cursor.to_list(length=None)
        out: List[MessageDBModel] = []
        for d in docs:
            msg = MessageDBModel(**d)
            msg._id = str(d["_id"])
            out.append(msg)
        return out

    async def find_by_client_message_id(self, chat_id: str, client_message_id: str) -> MessageDBModel | None:
        if not client_message_id:
            return None
        doc = await self._col.find_one({"chat_id": chat_id, "client_message_id": client_message_id})
        msg_db_model = MessageDBModel(**doc) if doc else None
        if msg_db_model:
            msg_db_model._id = str(doc["_id"])
            return msg_db_model
        else:
            return None

    async def recent_messages_window(self, chat_id: str) -> List[MessageDBModel]:
        cursor = self._col.find({"chat_id": chat_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        out: List[MessageDBModel] = []
        for doc in docs:
            msg = MessageDBModel(**doc)
            msg._id = str(doc["_id"])
            out.append(msg)
        return out

    async def delete(self, chat_id: str) -> bool:
        result = await self._col.delete_many({"chat_id": chat_id})
        return result.deleted_count > 0

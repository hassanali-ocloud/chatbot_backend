from typing import Any, Dict, List
from datetime import datetime
from bson import ObjectId
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MessageRepo:
    def __init__(self, db):
        self._col = db.get_collection("messages")

    async def create(self, chat_id: str, user_id: str, role: str, text: str, client_message_id: str | None = None):
        now = datetime.now()
        doc = {
            "chat_id": ObjectId(chat_id),
            "role": role,
            "text": text,
            "created_at": now,
            "client_message_id": client_message_id or None
        }
        res = await self._col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    async def list(self, chat_id: str, order: str = "asc"):
        oid = ObjectId(chat_id)
        sort_dir = 1 if order == "asc" else -1
        cursor = self._col.find({"chat_id": oid}).sort("created_at", sort_dir)
        docs = await cursor.to_list(length=None)
        for d in docs:
            d["_id"] = str(d["_id"])
            d["chat_id"] = str(d["chat_id"])
        return docs

    async def find_by_client_message_id(self, chat_id: str, client_message_id: str):
        if not client_message_id:
            return None
        oid = ObjectId(chat_id)
        doc = await self._col.find_one({"chat_id": oid, "client_message_id": client_message_id})
        return doc

    async def recent_messages_window(self, chat_id: str):
        oid = ObjectId(chat_id)
        cursor = self._col.find({"chat_id": oid}).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return list(reversed(docs))

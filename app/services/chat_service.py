from typing import List, Dict, Any, Optional
from app.db.chat_repo import ChatRepo
from app.db.message_repo import MessageRepo
from app.config.settings import settings
from app.utils.logger import get_logger
from app.utils.errors import NotFoundError, ProviderError

logger = get_logger(__name__)

class ChatService:
    def __init__(self, db):
        self.db = db
        self.chat_repo = ChatRepo(db)
        self.msg_repo = MessageRepo(db)

    async def create_chat(self, uid: str, title: Optional[str] = None) -> Dict[str, Any]:
        doc = await self.chat_repo.create(uid, title or "New chat")
        doc["id"] = str(doc["_id"])
        return {"id": doc["id"], "title": doc["title"], "created_at": doc["created_at"].isoformat(), "last_updated": doc["last_updated"].isoformat()}

    async def list_chats(self, uid: str) -> List[Dict[str, Any]]:
        docs = await self.chat_repo.list(uid)
        out = []
        for d in docs:
            out.append({
                "id": str(d["_id"]),
                "title": d.get("title"),
                "created_at": d.get("created_at").isoformat(),
                "last_updated": d.get("last_updated").isoformat()
            })
        return out

    async def get_messages(self, uid: str, chat_id: str, order: str = "asc") -> List[Dict[str, Any]]:
        chat = await self.chat_repo.get(uid, chat_id)
        if not chat:
            raise NotFoundError("chat not found")
        docs = await self.msg_repo.list(chat_id, order=order)
        return docs

    async def send_message(self, uid: str, chat_id: str, text: str, clientMessageId: Optional[str] = None) -> Dict[str, Any]:
        chat = await self.chat_repo.get(uid, chat_id)
        if not chat:
            raise NotFoundError("chat not found")

        if clientMessageId:
            existing = await self.msg_repo.find_by_client_message_id(chat_id, clientMessageId)
            if existing:
                msgs = await self.msg_repo.list(chat_id, order="asc")
                found_assistant = None
                for m in msgs:
                    if m.get("client_message_id") == clientMessageId:
                        idx = msgs.index(m)
                        for later in msgs[idx+1:]:
                            if later.get("role") == "assistant":
                                found_assistant = later
                                break
                        break
                return {"idempotent": True, "assistant": found_assistant, "original": existing}

        user_msg = await self.msg_repo.create(chat_id, uid, "user", text, client_message_id=clientMessageId)
        return {"messages": "Successfully created user message", "user_message_id": str(user_msg["_id"])}
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.db.chat_repo import ChatRepo
from app.db.message_repo import MessageRepo
from app.config.settings import settings
from app.config.enums import ProviderType, MessageRole
from app.db.models.chat_db_models import ChatDBModel
from app.providers.ollama_adapter import OllamaAdapter
from app.utils.logger import get_logger
from app.utils.errors import NotFoundError, ProviderError
from app.utils.serializers import to_serializable

logger = get_logger(__name__)

class ChatService:
    def _get_provider(self):
        if settings.CHAT_PROVIDER.upper() == ProviderType.OLLAMA.value:
            return OllamaAdapter()
    
    def __init__(self, db):
        self.db = db
        self.chat_repo = ChatRepo(db)
        self.msg_repo = MessageRepo(db)
        self.provider = self._get_provider()

    async def create_chat(self, uid: str, title: Optional[str] = None) -> dict[str, Any]:
        doc = await self.chat_repo.create(uid, title or "New chat")
        doc["id"] = str(doc["_id"])
        return {"id": doc["id"], "title": doc["title"], "created_at": doc["created_at"].isoformat(), "last_updated": doc["last_updated"].isoformat()}

    async def list_chats(self, uid: str) -> List[Dict[str, Any]]:
        docs = await self.chat_repo.list(uid)
        out = []
        for d in docs:
            created_at = d.get("created_at")
            last_updated = d.get("last_updated")

            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            if isinstance(last_updated, datetime):
                last_updated = last_updated.isoformat()

            out.append({
                "id": str(d["_id"]),
                "title": d.get("title"),
                "created_at": created_at,
                "last_updated": last_updated
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
                for m in msgs:
                    if m.get("client_message_id") == clientMessageId:
                        idx = msgs.index(m)
                        break
                return {"idempotent": True, "original": to_serializable(existing)}

        user_msg = await self.msg_repo.create(chat_id, uid, "user", text, client_message_id=clientMessageId)
        history = await self.msg_repo.recent_messages_window(chat_id)
        provider_msgs = []
        for m in history: 
            role = m.get("role")
            content = m.get("text")
            has_system_in_history = any(m.get("role") == MessageRole.SYSTEM.value for m in history)
            has_system_in_provider = any(msg.get("role") == MessageRole.SYSTEM.value for msg in provider_msgs)
            if not has_system_in_history and not has_system_in_provider:
                provider_msgs.insert(0, {"role": MessageRole.SYSTEM.value, "content": "You are a helpful chatbot assistant"})
            provider_msgs.append({"role": role, "content": content})
        if not provider_msgs or provider_msgs[-1].get("content") != text:
            provider_msgs.append({"role": MessageRole.SYSTEM.value, "content": "You are a helpful chatbot assistant"})
            provider_msgs.append({"role": MessageRole.USER.value, "content": text})

        try:
            provider_result = await self.provider.generate_reply(provider_msgs)
            assistant_text = provider_result.get("content")
        except Exception as e:
            logger.error("provider.generate_reply failed", extra={"err": str(e)})
            raise ProviderError("Provider call failed")

        assistant_msg = await self.msg_repo.create(chat_id, uid, MessageRole.ASSISTANT.value, assistant_text, client_message_id=None)
        await self.chat_repo.update(chat_id)

        return {MessageRole.ASSISTANT.value: {"id": str(assistant_msg["_id"]), "role": MessageRole.ASSISTANT.value, "text": assistant_msg["text"], "created_at": assistant_msg["created_at"].isoformat()},}

    async def delete_chat(self, chat_id: str) -> Dict[str, Any]:
        msg_status = await self.msg_repo.delete(chat_id)
        chat_status = await self.chat_repo.delete(chat_id)
        if not chat_status:
            raise NotFoundError("chat not found")
        return {"status": "deleted"}

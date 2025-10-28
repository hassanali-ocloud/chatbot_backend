from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config.constants import SYSTEM_INSTRUCTION
from app.db.chat_repo import ChatRepo
from app.db.message_repo import MessageRepo
from app.config.settings import settings
from app.config.enums import ProviderType, MessageRole
from app.providers.ollama_adapter import OllamaAdapter
from app.services.types.chat_types import ChatServiceModel
from app.services.types.message_types import MessageServiceModel
from app.utils.logger import get_logger
from app.utils.errors import NotFoundError, ProviderError
from app.utils.serializers import to_serializable
from app.mappers.chat_mapper import ChatMapper
from app.mappers.message_mapper import MessageMapper

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

    async def create_chat(self, uid: str, title: Optional[str] = None) -> ChatServiceModel:
        doc = await self.chat_repo.create(uid, title or "New chat")
        domain = ChatMapper.DBToDomain.map_one(doc)
        return domain

    async def list_chats(self, uid: str) -> List[ChatServiceModel]:
        docs = await self.chat_repo.list(uid)
        domain_model_list = ChatMapper.DBToDomain.map_list(docs)
        return domain_model_list

    async def get_messages(self, uid: str, chat_id: str, order: str = "asc") -> List[MessageServiceModel]:
        chat = await self.chat_repo.get(uid, chat_id)
        if not chat:
            raise NotFoundError("chat not found")
        docs = await self.msg_repo.list(chat_id, order=order)
        domain = MessageMapper.DBToDomain.map_list(docs)
        return domain

    async def send_message(self, uid: str, chat_id: str, text: str, clientMessageId: Optional[str] = None) -> Dict[str, Any] | MessageServiceModel:
        chat = await self.chat_repo.get(uid, chat_id)
        if not chat:
            raise NotFoundError("chat not found")

        chat_service_model = ChatMapper.DBToDomain.map_one(chat)

        if clientMessageId:
            existing = await self.msg_repo.find_by_client_message_id(chat_id, clientMessageId)
            if existing:
                msgs = await self.msg_repo.list(chat_id, order="asc")
                msgs_service_model = MessageMapper.DBToDomain.map_list(msgs)
                for m in msgs_service_model:
                    if m.client_message_id == clientMessageId:
                        break
                return {"idempotent": True, "original": to_serializable(existing)}

        await self.msg_repo.create(chat_id, uid, MessageRole.USER.value, text, client_message_id=clientMessageId)
        history = await self.msg_repo.recent_messages_window(chat_id)
        history_service_model = MessageMapper.DBToDomain.map_list(history)
        provider_msgs = []
        for m in history_service_model: 
            role = m.role
            content = m.text
            has_system_in_history = any(m.role == MessageRole.SYSTEM.value for m in history_service_model)
            has_system_in_provider = any(msg.get("role") == MessageRole.SYSTEM.value for msg in provider_msgs)
            if not has_system_in_history and not has_system_in_provider:
                provider_msgs.insert(0, {"role": MessageRole.SYSTEM.value, "content": SYSTEM_INSTRUCTION})
            provider_msgs.append({"role": role, "content": content})
        if not provider_msgs or provider_msgs[-1].get("content") != text:
            provider_msgs.append({"role": MessageRole.SYSTEM.value, "content": SYSTEM_INSTRUCTION})
            provider_msgs.append({"role": MessageRole.USER.value, "content": text})

        try:
            provider_response_model = await self.provider.generate_reply(provider_msgs)
            assistant_text = provider_response_model.content
        except Exception as e:
            logger.error("provider.generate_reply failed", extra={"err": str(e)})
            raise ProviderError("Provider call failed")

        assistant_msg = await self.msg_repo.create(chat_id, uid, MessageRole.ASSISTANT.value, assistant_text, client_message_id=None)
        assistant_msg_domain_model = MessageMapper.DBToDomain.map_one(assistant_msg)
        await self.chat_repo.update(chat_id)

        return assistant_msg_domain_model

    async def delete_chat(self, chat_id: str) -> Dict[str, Any]:
        msg_status = await self.msg_repo.delete(chat_id)
        chat_status = await self.chat_repo.delete(chat_id)
        if not chat_status:
            raise NotFoundError("chat not found")
        return {"status": "deleted"}

from typing import List
from app.db.models.chat_db_models import ChatDBModel
from app.services.types.chat_types import ChatServiceModel
from app.schemas.chat import ChatResponse

class ChatMapper:
    class DBToDomain:
        @staticmethod
        def map_one(doc: ChatDBModel) -> ChatServiceModel:
            return ChatServiceModel(
                id=str(doc._id),
                user_id=doc.user_id,
                title=doc.title,
                created_at=doc.created_at,
                last_updated=doc.last_updated,
            )

        @staticmethod
        def map_list(docs: List[ChatDBModel]) -> List[ChatServiceModel]:
            return [ChatMapper.DBToDomain.map_one(d) for d in docs]

    class DomainToAPI:
        @staticmethod
        def map_one(chat: ChatServiceModel) -> ChatResponse:
            return ChatResponse(
                id=str(chat.id),
                user_id=chat.user_id,
                title=chat.title,
                created_at=chat.created_at.isoformat(),
                last_updated=chat.last_updated.isoformat(),
            )

        @staticmethod
        def map_list(chats: List[ChatServiceModel]) -> List[ChatResponse]:
            return [ChatMapper.DomainToAPI.map_one(c) for c in chats]
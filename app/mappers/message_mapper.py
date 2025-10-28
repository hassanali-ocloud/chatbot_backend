from typing import List
from app.db.models.message_db_models import MessageDBModel
from app.services.types.message_types import MessageServiceModel
from app.schemas.message import MessageResponse

class MessageMapper:
    class DBToDomain:
        @staticmethod
        def map_one(doc: MessageDBModel) -> MessageServiceModel:
            return MessageServiceModel(
                id=str(doc._id),
                chat_id=doc.chat_id,
                user_id=doc.user_id,
                role=doc.role,
                text=doc.text,
                created_at=doc.created_at,
                client_message_id=doc.client_message_id,
            )

        @staticmethod
        def map_list(docs: List[MessageDBModel]) -> List[MessageServiceModel]:
            return [MessageMapper.DBToDomain.map_one(d) for d in docs]

    class DomainToAPI:
        @staticmethod
        def map_one(message: MessageServiceModel) -> MessageResponse:
            res = MessageResponse(
                id=str(message.id),
                chat_id=message.chat_id,
                user_id=message.user_id,
                role=message.role,
                text=message.text,
                created_at=message.created_at.isoformat(),
            )
            return res

        @staticmethod
        def map_list(messages: List[MessageServiceModel]) -> List[MessageResponse]:
            return [MessageMapper.DomainToAPI.map_one(m) for m in messages]
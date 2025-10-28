from typing import Protocol, List, Dict, Any
from app.providers.types.provider_types import ProviderResponseModel

class ChatProvider(Protocol):
    async def generate_reply(self, messages: List[Dict[str, Any]], options: Dict[str, Any] = {}) -> ProviderResponseModel:
        ...

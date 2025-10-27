from typing import Protocol, List, Dict, Any

class ChatProvider(Protocol):
    async def generate_reply(self, messages: List[Dict[str, Any]], options: Dict[str, Any] = {}) -> Dict[str, Any]:
        ...

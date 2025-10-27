import httpx
from typing import List, Dict, Any
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class OllamaAdapter:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OLLAMA_API_KEY
        if not self.api_key:
            logger.info("Ollama API key not set; OllamaAdapter created but will error on calls")

    async def generate_reply(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.api_key:
            return {"content": "Ollama key missing"}

        payload = {
            "model": "phi3",
            "messages": [{"role": m.get("role"), "content": m.get("content")} for m in messages],
            "stream": False,
        }

        headers = {"Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(settings.OLLAMA_CHAT_URL, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                content = data["message"]["content"]
                return {"content": content}
            except httpx.RequestError as e:
                logger.error("Ollama request failed", extra={"err": str(e)})
                raise
            except httpx.HTTPStatusError as e:
                logger.error("Ollama HTTP error", extra={"status": e.response.status_code, "text": e.response.text})
                raise

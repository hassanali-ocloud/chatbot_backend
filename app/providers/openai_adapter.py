from typing import List, Dict, Any
from app.config.settings import settings
from app.providers.types.provider_types import ProviderResponseModel
from app.utils.logger import get_logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langsmith import Client

logger = get_logger(__name__)

class OpenAIAdapter:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not set; OpenAIAdapter will fail on calls")

        self.langsmith_client = Client()
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=settings.OPENAI_MODEL,
            temperature=0.7,
        )

    async def generate_reply(self, messages: List[Dict[str, Any]]) -> ProviderResponseModel:
        if not self.api_key:
            return ProviderResponseModel(content="OpenAI API key missing")

        try:
            message_objs = [{"role": m.get("role"), "content": m.get("content")} for m in messages]
            response = await self.llm.ainvoke(message_objs)
            return ProviderResponseModel(content=response.content)

        except Exception as e:
            logger.error("OpenAIAdapter Error", extra={"err": str(e)})
            return ProviderResponseModel(content=f"Error from OpenAI: {str(e)}")

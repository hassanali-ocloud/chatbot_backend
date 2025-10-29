from enum import Enum

class ProviderType(str, Enum):
    OLLAMA = "OLLAMA"
    OPENAI = "OPENAI"

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

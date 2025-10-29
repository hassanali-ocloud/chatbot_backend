from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from io import StringIO

app_env = os.getenv("APP_ENV")
env_file = f".env.{app_env}" if app_env else ".env"

if app_env:
    load_dotenv(env_file)

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    FRONTEND_URL: str
    FRONTEND_URL_2: str
    OLLAMA_API_KEY: str
    CHAT_PROVIDER: str
    OLLAMA_CHAT_URL: str
    FIREBASE_CREDENTIALS: str
    LANGCHAIN_TRACING_V2: bool
    LANGCHAIN_PROJECT: str
    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    OPENAI_MODEL: str

    class Config:
        env_file = env_file

settings = Settings()

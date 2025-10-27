from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from io import StringIO

app_env = os.getenv("APP_ENV")
env_file = f".env.{app_env}" if app_env else ".env"

if app_env and not os.path.exists(env_file):
    load_dotenv(stream=StringIO(app_env))

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    FRONTEND_URL: str
    FRONTEND_URL_2: str
    OLLAMA_API_KEY: str
    CHAT_PROVIDER: str
    OLLAMA_CHAT_URL: str

    class Config:
        env_file = env_file

settings = Settings()

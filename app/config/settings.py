import os
import json
import boto3
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

def load_aws_secret():
    secret_name = os.getenv("AWS_SECRET_NAME")
    if not secret_name:
        return {}

    region_name = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString")
        return json.loads(secret_string) if secret_string else {}
    except Exception as e:
        print(f"⚠️ Could not load secrets from AWS Secrets Manager: {e}")
        return {}

app_env = os.getenv("APP_ENV")
env_file = f".env.{app_env}" if app_env else ".env"

if os.path.exists(env_file):
    print(f"✅ Loading environment file: {env_file}")
    load_dotenv(env_file)
    aws_secrets = {}
else:
    # On AWS (no .env file) → load from Secrets Manager
    print("🌐 No .env file found — loading from AWS Secrets Manager")
    aws_secrets = load_aws_secret()

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    FRONTEND_URL: str
    FRONTEND_URL_2: str
    OLLAMA_API_KEY: str
    CHAT_PROVIDER: str
    OLLAMA_CHAT_URL: str
    LANGCHAIN_TRACING_V2: bool
    LANGCHAIN_PROJECT: str
    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    OPENAI_MODEL: str
    FIREBASE_CREDENTIALS: str
    APP_ENV: str = app_env or "production"

    class Config:
        env_file = env_file

# Create settings instance
settings = Settings(**aws_secrets)

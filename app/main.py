from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.connection import init_db
from app.api.v1.routes import chat_routes as chat_router_v1
from app.utils.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Db connection")
    await init_db()
    yield
    logger.info("Cleaning up resources")

app = FastAPI(title="Chatbot Backend", lifespan=lifespan)

app.include_router(chat_router_v1.router, prefix="/v1", tags=["chat-v1"])

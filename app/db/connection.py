from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.utils.logger import get_logger

_logger = get_logger(__name__)
_client = None
_db = None

async def init_db():
    global _client, _db
    if _client:
        return
    _client = AsyncIOMotorClient(settings.MONGO_URI)
    _db = _client[settings.DB_NAME]
    await _ensure_indexes()
    _logger.info("Connected to MongoDB", extra={"uri": settings.MONGO_URI, "db": settings.DB_NAME})

def get_client():
    if not _client:
        raise RuntimeError("MongoDB client not initialized; call init_db first")
    return _client

async def get_db():
    if _db is None:
        await init_db()
    return _db

async def _ensure_indexes():
    db = _client[settings.DB_NAME]
    chats = db.get_collection("chats")
    messages = db.get_collection("messages")
    await chats.create_index([("user_id", 1), ("last_updated", -1)])
    await messages.create_index([("chat_id", 1), ("created_at", 1)])
    await messages.create_index([("message_id", 1)], unique=False)
    _logger.info("Ensured MongoDB indexes")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.connection import init_db
from app.api.v1.routes import chat_routes as chat_router_v1
from app.utils.logger import get_logger
from app.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Db connection")
    await init_db()
    yield
    logger.info("Cleaning up resources")

app = FastAPI(title="Chatbot Backend", lifespan=lifespan)

origins = [
    settings.FRONTEND_URL,  # Vite default port
    settings.FRONTEND_URL_2,  # Some browsers resolve localhost to 127.0.0.1
]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Allowed origins
    allow_credentials=True,       # Allow cookies, auth headers, etc.
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all request headers
)

app.include_router(chat_router_v1.router, prefix="/v1", tags=["chat-v1"])

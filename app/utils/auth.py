import os
import firebase_admin
from firebase_admin import credentials, auth
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_firebase_initialized = False

def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return

    cred_path = settings.FIREBASE_CREDENTIALS
    if not cred_path:
        raise RuntimeError("FIREBASE_CREDENTIALS env var not set")
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Initialized Firebase Admin with service account", extra={"cred_path": cred_path})
    except Exception as e:
        logger.error("Failed to init firebase admin SDK", extra={"err": str(e)})
        raise

async def verify_id_token(authorization_header: str) -> str:
    _init_firebase()
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Authorization header must be 'Bearer <token>'")
    token = authorization_header.split("Bearer ")[1]
    decoded = auth.verify_id_token(token)
    uid = decoded.get("uid")
    if not uid:
        raise ValueError("Invalid token: no uid")
    return uid

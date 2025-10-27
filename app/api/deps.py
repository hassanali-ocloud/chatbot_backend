from fastapi import Depends, Header, HTTPException, status
from typing import Optional
from app.db.connection import get_db
from app.utils.auth import verify_id_token

async def get_uid(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    try:
        uid = await verify_id_token(authorization)
        return uid
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

async def db():
    return await get_db()

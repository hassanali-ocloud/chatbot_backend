from fastapi import Depends, Header, HTTPException, status
from typing import Optional
from app.db.connection import get_db

async def db():
    return await get_db()

from app.api.v1.endpoints import chat
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(chat.router, tags=["chat"])

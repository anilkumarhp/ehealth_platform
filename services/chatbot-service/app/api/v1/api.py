from fastapi import APIRouter

from app.api.v1.routers import chat, conversations

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
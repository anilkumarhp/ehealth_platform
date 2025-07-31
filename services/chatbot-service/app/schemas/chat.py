from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    user_id: Optional[str] = None

class Conversation(ConversationBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    messages: List[Message] = []
    
    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    messages: List[MessageBase]
    conversation_id: Optional[str] = None
    max_tokens: int = 256
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
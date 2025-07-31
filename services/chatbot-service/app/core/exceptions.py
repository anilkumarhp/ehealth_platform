from fastapi import HTTPException
from typing import Any, Dict, Optional

class ChatbotException(HTTPException):
    """Base exception for chatbot service"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class LLMServiceException(ChatbotException):
    """Exception raised when LLM service fails"""
    def __init__(self, detail: str = "LLM service error"):
        super().__init__(status_code=503, detail=detail)

class ExternalServiceException(ChatbotException):
    """Exception raised when an external service fails"""
    def __init__(self, service_name: str, detail: str = "External service error"):
        super().__init__(status_code=503, detail=f"{service_name} service error: {detail}")

class ConversationNotFoundException(ChatbotException):
    """Exception raised when a conversation is not found"""
    def __init__(self, conversation_id: str):
        super().__init__(status_code=404, detail=f"Conversation {conversation_id} not found")

class InvalidInputException(ChatbotException):
    """Exception raised when input is invalid"""
    def __init__(self, detail: str = "Invalid input"):
        super().__init__(status_code=400, detail=detail)
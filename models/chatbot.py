from pydantic import BaseModel, EmailStr
from typing import Optional


class WebChatRequest(BaseModel):
    """Web chat request model for multi-step conversation flow"""
    message: str
    session_id: str


class WebChatResponse(BaseModel):
    """Web chat response model with state information"""
    answer: str
    state: str
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    session_reset: bool = False


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    business_id: str
    thread_id: str  # Conversation ID (unique per user session)
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    route: str = "conversation"  # Default to "conversation" if not set
    email_sent: bool

    # Business information
    business_name: str
    business_email: Optional[str] = None

    # User contact information (extracted during conversation)
    user_email: Optional[str] = None
    user_phone: Optional[str] = None

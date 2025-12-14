from pydantic import BaseModel, EmailStr
from typing import Optional

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
    needs_contact_info: bool
    email_sent: bool
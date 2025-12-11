from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WhatsAppSession(BaseModel):
    whatsapp_number: str
    business_id: Optional[str] = None
    conversation_history: list = []
    active: bool = True
    created_at: Optional[datetime] = None
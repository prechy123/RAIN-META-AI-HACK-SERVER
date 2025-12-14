"""
Chatbot routes for SharpChat AI
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from agent.main_agent import main_agent
from models.chatbot import ChatRequest, ChatResponse
logger = logging.getLogger("chatbot_routes")

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint - handles FAQ, Support, and Conversation queries.
    """
    try:
        logger.info(f"Processing chat for business {request.business_id}, thread {request.thread_id}")
        
        # Invoke main agent (auto-fetches business_name and business_email)
        result = await main_agent(
            query=request.message,
            business_id=request.business_id,
            thread_id=request.thread_id,
            user_email=request.user_email,
            user_phone=request.user_phone
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



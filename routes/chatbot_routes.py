"""
Chatbot routes for AlatChat AI
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone
import uuid
from agent.main_agent import main_agent
from models.chatbot import ChatRequest, ChatResponse, WebChatRequest, WebChatResponse
from config.database import session_collection
from routes.utils.session_utils import (
    SessionState,
    is_exit_command,
    find_business_by_id,
    find_business_by_name
)

logger = logging.getLogger("chatbot_routes")

router = APIRouter()


def get_or_create_web_session(session_id: str) -> dict:
    """Get existing web session or create new one"""
    session = session_collection.find_one({"web_session_id": session_id})

    if not session:
        session = {
            "web_session_id": session_id,
            "state": SessionState.INITIAL,
            "name": None,
            "business_id": None,
            "thread_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        session_collection.insert_one(session)
        logger.info(f"Created new web session for {session_id}")

    return session


def update_web_session(session_id: str, updates: dict):
    """Update web session with new data"""
    updates["updated_at"] = datetime.now(timezone.utc)
    session_collection.update_one(
        {"web_session_id": session_id},
        {"$set": updates}
    )


@router.post("/web-chat", response_model=WebChatResponse)
async def web_chat(request: WebChatRequest) -> WebChatResponse:
    """
    Web chat endpoint with multi-step conversation flow
    Handles: name collection → business selection → AI chatbot
    """
    try:
        incoming_msg = request.message.strip()
        session_id = request.session_id

        logger.info(
            f"Received web chat message from session {session_id}: {incoming_msg}")

        # Handle empty messages
        if not incoming_msg:
            return WebChatResponse(
                answer="Please send a message to continue.",
                state=SessionState.INITIAL
            )

        # Get or create session
        session = get_or_create_web_session(session_id)
        current_state = session.get("state", SessionState.INITIAL)

        # Check for exit/reset commands (works in any state except INITIAL)
        if current_state != SessionState.INITIAL and is_exit_command(incoming_msg):
            user_name = session.get("name", "there")

            # Delete the session to start fresh
            session_collection.delete_one({"web_session_id": session_id})

            logger.info(f"Web session {session_id} ended by user")
            return WebChatResponse(
                answer=f"Session ended! Thanks for chatting, {user_name}. Your conversation has been reset. To start a new conversation, just send me any message.",
                state=SessionState.INITIAL,
                session_reset=True
            )

        # State machine for conversation flow
        if current_state == SessionState.INITIAL:
            # First interaction - ask for name
            update_web_session(
                session_id, {"state": SessionState.AWAITING_NAME})
            return WebChatResponse(
                answer="Welcome to AlatChat AI! 👋\n\nWhat's your name?\n\n💡 Type 'exit' anytime to start over.",
                state=SessionState.AWAITING_NAME
            )

        elif current_state == SessionState.AWAITING_NAME:
            # Store name and ask for business
            user_name = incoming_msg
            update_web_session(session_id, {
                "state": SessionState.AWAITING_BUSINESS,
                "name": user_name
            })
            return WebChatResponse(
                answer=f"Nice to meet you, {user_name}! 😊\n\nWhich business would you like to chat with?\n\n💡 You can enter:\n• Business ID (e.g., BUS-0001)\n• Business name (e.g., Joe's Coffee Shop)",
                state=SessionState.AWAITING_BUSINESS
            )

        elif current_state == SessionState.AWAITING_BUSINESS:
            # Search for business
            business = None

            # Check if it's a business ID (format: BUS-XXXX)
            if incoming_msg.upper().startswith("BUS-"):
                business = find_business_by_id(incoming_msg.upper())
            else:
                # Search by name with fuzzy matching
                business = find_business_by_name(incoming_msg)

            if business:
                # Business found - generate thread_id and connect to chatbot
                thread_id = f"web_{session_id}_{uuid.uuid4().hex[:8]}"
                business_id = business.get("business_id")
                business_name = business.get("businessName")
                business_desc = business.get("businessDescription", "")

                update_web_session(session_id, {
                    "state": SessionState.CHATTING,
                    "business_id": business_id,
                    "thread_id": thread_id
                })

                logger.info(
                    f"Web session {session_id} connected to business {business_id} with thread {thread_id}")

                return WebChatResponse(
                    answer=f"✅ Great! You're now connected to {business_name}\n\n{business_desc}\n\nHow can I help you today?\n\n_Type 'change business' to switch or 'exit' to end._",
                    state=SessionState.CHATTING,
                    business_name=business_name,
                    business_description=business_desc
                )
            else:
                # No business found
                return WebChatResponse(
                    answer=f"❌ Sorry, I couldn't find a business matching '{incoming_msg}'.\n\nPlease try again with:\n• A different business name\n• A business ID (format: BUS-XXXX)",
                    state=SessionState.AWAITING_BUSINESS
                )

        elif current_state == SessionState.CHATTING:
            # User is chatting with business - route to chatbot
            business_id = session.get("business_id")
            thread_id = session.get("thread_id")
            user_name = session.get("name")

            if not business_id or not thread_id:
                # Session corrupted - reset
                update_web_session(session_id, {
                    "state": SessionState.AWAITING_NAME,
                    "business_id": None,
                    "thread_id": None
                })
                return WebChatResponse(
                    answer="Sorry, there was an error with your session. Let's start over.\n\nWhat's your name?",
                    state=SessionState.AWAITING_NAME
                )

            try:
                # Call the main agent
                result = await main_agent(
                    query=incoming_msg,
                    business_id=business_id,
                    thread_id=thread_id,
                    user_email=None,
                    user_phone=None
                )

                # Send agent's response
                answer = result.get(
                    "answer", "I'm not sure how to help with that.")
                business_name = result.get("business_name", "")

                logger.info(
                    f"Agent responded to web session {session_id} via {result.get('route', 'unknown')} route")

                return WebChatResponse(
                    answer=answer,
                    state=SessionState.CHATTING,
                    business_name=business_name
                )

            except Exception as e:
                logger.error(f"Error calling agent: {e}", exc_info=True)
                return WebChatResponse(
                    answer="Sorry, I encountered an error processing your message. Please try again or contact support.",
                    state=SessionState.CHATTING
                )

        else:
            # Unknown state - reset
            update_web_session(session_id, {
                "state": SessionState.AWAITING_NAME,
                "business_id": None,
                "thread_id": None,
                "name": None
            })
            return WebChatResponse(
                answer="Sorry, something went wrong. Let's start over.\n\nWhat's your name?",
                state=SessionState.AWAITING_NAME
            )

    except Exception as e:
        logger.error(f"Error in web chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry, there was an error processing your message."
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint - handles FAQ, Support, and Conversation queries.
    """
    try:
        logger.info(
            f"Processing chat for business {request.business_id}, thread {request.thread_id}")

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

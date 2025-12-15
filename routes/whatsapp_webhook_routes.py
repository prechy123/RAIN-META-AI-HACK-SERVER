"""
WhatsApp Webhook routes for SharpChat AI
Handles multi-step conversation flow with Twilio integration
"""
import logging
from fastapi import APIRouter, Request, Response, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
from config.database import business_collection, session_collection
from datetime import datetime, timezone
from difflib import SequenceMatcher
import uuid
from agent.main_agent import main_agent

logger = logging.getLogger("whatsapp_webhook")

router = APIRouter()

# Session states


class SessionState:
    INITIAL = "INITIAL"
    AWAITING_NAME = "AWAITING_NAME"
    AWAITING_BUSINESS = "AWAITING_BUSINESS"
    CHATTING = "CHATTING"


def is_exit_command(message: str) -> bool:
    """Check if message is a command to end/reset session"""
    exit_commands = ['exit', 'quit', 'end', 'stop', 'restart', 'reset', 'new', 'change business', 'switch business']
    return message.lower().strip() in exit_commands


def get_or_create_session(whatsapp_number: str) -> dict:
    """Get existing session or create new one"""
    session = session_collection.find_one({"whatsapp_number": whatsapp_number})

    if not session:
        session = {
            "whatsapp_number": whatsapp_number,
            "state": SessionState.INITIAL,
            "name": None,
            "business_id": None,
            "thread_id": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        session_collection.insert_one(session)
        logger.info(f"Created new session for {whatsapp_number}")

    return session


def update_session(whatsapp_number: str, updates: dict):
    """Update session with new data"""
    updates["updated_at"] = datetime.now(timezone.utc)
    session_collection.update_one(
        {"whatsapp_number": whatsapp_number},
        {"$set": updates}
    )


def find_business_by_id(business_id: str) -> dict:
    """Find business by exact ID match"""
    return business_collection.find_one({"business_id": business_id})


def find_business_by_name(search_term: str, threshold: float = 0.6) -> dict:
    """
    Find business by name using fuzzy matching
    Returns the closest match if similarity >= threshold
    """
    businesses = list(business_collection.find({}))

    if not businesses:
        return None

    best_match = None
    best_ratio = 0

    search_term_lower = search_term.lower().strip()

    for business in businesses:
        business_name = business.get("businessName", "").lower().strip()

        # Calculate similarity ratio
        ratio = SequenceMatcher(None, search_term_lower, business_name).ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_match = business

    # Return match only if similarity meets threshold
    if best_ratio >= threshold:
        logger.info(
            f"Found business match: '{best_match.get('businessName')}' with {best_ratio:.2%} similarity")
        return best_match

    logger.info(
        f"No business match found for '{search_term}' (best: {best_ratio:.2%})")
    return None


@router.post("/")
async def whatsapp_webhook(request: Request):
    """
    Main webhook endpoint for Twilio WhatsApp messages
    Handles multi-step conversation flow
    """
    try:
        form_data = await request.form()

        # Extract message details
        incoming_msg = form_data.get('Body', '').strip()
        from_number = form_data.get('From', '')

        logger.info(f"Received message from {from_number}: {incoming_msg}")

        # Create Twilio response
        resp = MessagingResponse()

        # Handle empty messages
        if not incoming_msg:
            resp.message("Please send a message to continue.")
            return Response(content=str(resp), media_type="application/xml")

        # Get or create session
        session = get_or_create_session(from_number)
        current_state = session.get("state", SessionState.INITIAL)
        
        # Check for exit/reset commands (works in any state except INITIAL)
        if current_state != SessionState.INITIAL and is_exit_command(incoming_msg):
            user_name = session.get("name", "there")
            
            # Delete the session to start fresh
            session_collection.delete_one({"whatsapp_number": from_number})
            
            resp.message(
                f"👋 Session ended!\n\n"
                f"Thanks for chatting, {user_name}! Your conversation has been reset.\n\n"
                f"To start a new conversation, just send me any message.\n\n"
                f"💡 Tip: You can type 'exit', 'quit', 'restart', or 'change business' anytime to start over."
            )
            
            logger.info(f"User {from_number} ended their session")
            return Response(content=str(resp), media_type="application/xml")

        # State machine for conversation flow
        if current_state == SessionState.INITIAL:
            # First interaction - ask for name
            resp.message(
                "Welcome to SharpChat AI! 👋\n\n"
                "What's your name?\n\n"
                "💡 Type 'exit' anytime to start over."
            )
            update_session(from_number, {"state": SessionState.AWAITING_NAME})

        elif current_state == SessionState.AWAITING_NAME:
            # Store name and ask for business
            user_name = incoming_msg
            resp.message(
                f"Nice to meet you, {user_name}! 😊\n\n"
                f"Which business would you like to chat with?\n\n"
                f"💡 You can enter:\n"
                f"• Business ID (e.g., BUS-0001)\n"
                f"• Business name (e.g., Joe's Coffee Shop)"
            )
            update_session(from_number, {
                "state": SessionState.AWAITING_BUSINESS,
                "name": user_name
            })

        elif current_state == SessionState.AWAITING_BUSINESS:
            # Search for business
            business = None

            # Check if it's a business ID (format: BUS-XXXX)
            if incoming_msg.upper().startswith("BUS-"):
                business = find_business_by_id(incoming_msg.upper())
                search_type = "ID"
            else:
                # Search by name with fuzzy matching
                business = find_business_by_name(incoming_msg)
                search_type = "name"

            if business:
                # Business found - generate thread_id and connect to chatbot
                thread_id = f"whatsapp_{from_number}_{uuid.uuid4().hex[:8]}"
                business_id = business.get("business_id")
                business_name = business.get("businessName")
                business_desc = business.get("businessDescription", "")

                resp.message(
                    f"✅ Great! You're now connected to *{business_name}*\n\n"
                    f"{business_desc}\n\n"
                    f"How can I help you today?\n\n"
                    f"_Type 'change business' to switch or 'exit' to end._"
                )

                update_session(from_number, {
                    "state": SessionState.CHATTING,
                    "business_id": business_id,
                    "thread_id": thread_id
                })

                logger.info(
                    f"User connected to business {business_id} with thread {thread_id}")
            else:
                # No business found
                resp.message(
                    f"❌ Sorry, I couldn't find a business matching '{incoming_msg}'.\n\n"
                    f"Please try again with:\n"
                    f"• A different business name\n"
                    f"• A business ID (format: BUS-XXXX)"
                )

        elif current_state == SessionState.CHATTING:
            # User is chatting with business - route to chatbot
            business_id = session.get("business_id")
            thread_id = session.get("thread_id")
            user_name = session.get("name")

            if not business_id or not thread_id:
                # Session corrupted - reset
                resp.message(
                    "Sorry, there was an error with your session. Let's start over.\n\n"
                    "What's your name?"
                )
                update_session(from_number, {
                    "state": SessionState.AWAITING_NAME,
                    "business_id": None,
                    "thread_id": None
                })
            else:
                try:
                    # Call the main agent
                    result = await main_agent(
                        query=incoming_msg,
                        business_id=business_id,
                        thread_id=thread_id,
                        user_email=None,  # WhatsApp doesn't provide email
                        user_phone=from_number
                    )

                    # Send agent's response
                    answer = result.get(
                        "answer", "I'm not sure how to help with that.")
                    resp.message(answer)

                    logger.info(
                        f"Agent responded to {from_number} via {result.get('route', 'unknown')} route")

                except Exception as e:
                    logger.error(f"Error calling agent: {e}", exc_info=True)
                    resp.message(
                        "Sorry, I encountered an error processing your message. "
                        "Please try again or contact support."
                    )

        else:
            # Unknown state - reset
            resp.message(
                "Sorry, something went wrong. Let's start over.\n\n"
                "What's your name?"
            )
            update_session(from_number, {
                "state": SessionState.AWAITING_NAME,
                "business_id": None,
                "thread_id": None,
                "name": None
            })

        return Response(content=str(resp), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error in webhook: {e}", exc_info=True)
        resp = MessagingResponse()
        resp.message("Sorry, there was an error processing your message.")
        return Response(content=str(resp), media_type="application/xml")


@router.get("/session/{whatsapp_number}")
async def get_session(whatsapp_number: str):
    """
    Get session details for debugging
    """
    session = session_collection.find_one(
        {"whatsapp_number": whatsapp_number},
        {"_id": 0}
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.post("/reset-session")
async def reset_session(whatsapp_number: str):
    """
    Reset a user's session
    """
    result = session_collection.delete_one(
        {"whatsapp_number": whatsapp_number})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session reset successfully"}

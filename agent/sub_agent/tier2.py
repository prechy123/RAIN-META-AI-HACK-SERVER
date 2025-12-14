"""
Tier 2 Handler - Human Support Requests
LLM-powered conversational flow for collecting contact info
"""
import logging
import re
from langchain_core.messages import AIMessage
from agent.llm import get_llm
from agent.email_service import send_support_email
from agent.graph_builder.agent_state import AgentState
from agent.agent_utils import format_chat_history, get_last_user_message

logger = logging.getLogger("tier2")


def extract_email(text: str) -> str:
    """Extract email address from text using regex."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str:
    """Extract phone number from text using regex."""
    # Matches formats like: +234..., 0..., +1..., etc.
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,}'
    match = re.search(phone_pattern, text)
    if match:
        # Clean up the phone number
        phone = match.group(0)
        # Remove spaces, dashes, parentheses
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        return phone
    return None


async def Tier2(state: AgentState) -> dict:
    """
    Handle Tier 2 queries (human support requests) using LLM for conversation.
    
    Flow:
    1. Use LLM to have natural conversation
    2. Extract contact preferences and info from conversation
    3. Send email when we have sufficient info
    
    Returns dict to update state.
    """
    try:
        # Extract state variables
        user_email = state.get("user_email")
        user_phone = state.get("user_phone")
        preferred_contact_method = state.get("preferred_contact_method")
        business_name = state.get("business_name", "this business")
        business_email = state.get("business_email")
        
        # Filter out placeholder values from the request
        if user_email in ["user@example.com", None, ""]:
            user_email = None
        if user_phone in ["string", None, ""]:
            user_phone = None
        
        # Get conversation history and last user message
        conversation_history = format_chat_history(state["messages"])
        last_user_msg = get_last_user_message(state["messages"])
        
        # Extract contact info from USER messages only (not AI responses)
        from langchain_core.messages import HumanMessage
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        
        if not user_email:
            for msg in user_messages:
                msg_content = msg.content if hasattr(msg, 'content') else str(msg)
                extracted_email = extract_email(msg_content)
                # Ignore placeholder emails
                if extracted_email and extracted_email != "user@example.com":
                    user_email = extracted_email
                    logger.info(f"Extracted email: {user_email}")
                    break
        
        if not user_phone:
            for msg in user_messages:
                msg_content = msg.content if hasattr(msg, 'content') else str(msg)
                extracted_phone = extract_phone(msg_content)
                # Ignore placeholder phones
                if extracted_phone and extracted_phone not in ["string", "null"]:
                    user_phone = extracted_phone
                    logger.info(f"Extracted phone: {user_phone}")
                    break
        
        # Use LLM to determine contact preference if not set
        if not preferred_contact_method:
            llm = get_llm()
            
            analysis_prompt = f"""Analyze this user message and determine their preferred contact method.

User message: "{last_user_msg}"

Determine if they want to be contacted via:
- "email" (if they mention email, mail, or provide an email address)
- "phone" (if they mention phone, call, or provide a phone number)
- "both" (if they mention both or want multiple contact methods)
- "unknown" (if unclear)

Respond with ONLY one word: email, phone, both, or unknown"""

            analysis_response = await llm.ainvoke(analysis_prompt)
            detected_method = analysis_response.content.strip().lower()
            
            if detected_method in ["email", "phone", "both"]:
                preferred_contact_method = detected_method
                logger.info(f"LLM detected contact preference: {preferred_contact_method}")
        
        # Check if we have enough information to send email
        has_email = bool(user_email)
        has_phone = bool(user_phone)
        
        # Determine if we can proceed
        can_send_email = False
        if preferred_contact_method == "email" and has_email:
            can_send_email = True
        elif preferred_contact_method == "phone" and has_phone:
            can_send_email = True
        elif preferred_contact_method == "both" and has_email and has_phone:
            can_send_email = True
        
        # If we can send email, do it
        if can_send_email:
            logger.info(f"Sufficient contact info collected - sending email to {business_email}")
            
            # Generate conversation summary
            llm = get_llm()
            
            # Extract the main customer issue
            issue_prompt = f"""Extract the main customer issue or request from this conversation in 1 sentence.
Focus on WHAT the customer needs help with, not the contact collection process.

CONVERSATION:
{conversation_history}

MAIN ISSUE:"""
            
            issue_response = await llm.ainvoke(issue_prompt)
            main_issue = issue_response.content.strip()
            
            # Generate conversation summary
            summary_prompt = f"""Summarize this customer support conversation in 2-3 sentences.
Focus on what the customer needs and key details.

CONVERSATION:
{conversation_history}

BRIEF SUMMARY:"""
            
            summary_response = await llm.ainvoke(summary_prompt)
            conversation_summary = summary_response.content.strip()
            
            # Send email to business owner
            email_sent = False
            
            if business_email:
                logger.info(f"Sending support email to {business_email}")
                email_sent = await send_support_email(
                    business_name=business_name,
                    business_email=business_email,
                    user_email=user_email or "Not provided",
                    user_phone=user_phone or "Not provided",
                    conversation_summary=conversation_summary,
                    support_request=main_issue  # Use extracted issue instead of last message
                )
            else:
                logger.warning(f"No business email found - cannot send notification")
            
            # Generate success response using LLM
            success_prompt = f"""Generate a friendly confirmation message for a customer.

Context:
- Business: {business_name}
- Customer wants to be contacted via: {preferred_contact_method}
- Customer email: {user_email or 'not provided'}
- Customer phone: {user_phone or 'not provided'}
- Email sent to business: {email_sent}

Generate a warm, professional message confirming:
1. Their request has been sent to the business
2. How the business will contact them
3. Their contact details
4. Ask if there's anything else you can help with

Keep it friendly and concise (2-3 sentences)."""

            response = await llm.ainvoke(success_prompt)
            
            return {
                "messages": [AIMessage(content=response.content)],
                "email_sent": email_sent,
                "user_email": user_email,
                "user_phone": user_phone,
                "preferred_contact_method": preferred_contact_method,
                "route": "tier2"
            }
        
        # We don't have enough info yet - use LLM to ask for it naturally
        else:
            llm = get_llm()
            
            # Build context for LLM
            context = f"""You are helping a customer who wants to speak with someone from {business_name}.

Current situation:
- Preferred contact method: {preferred_contact_method or 'not specified'}
- Has email: {has_email}
- Has phone: {has_phone}

Conversation so far:
{conversation_history}

Your task:
Generate a friendly, natural response that:
1. If contact preference unknown: Ask how they'd like to be contacted (email, phone, or both)
2. If preference is email but no email: Ask for their email address
3. If preference is phone but no phone: Ask for their phone number
4. If preference is both but missing either: Ask for the missing info

Be conversational and warm. Don't be robotic. Keep it brief (1-2 sentences)."""

            response = await llm.ainvoke(context)
            
            return {
                "messages": [AIMessage(content=response.content)],
                "email_sent": False,
                "user_email": user_email,
                "user_phone": user_phone,
                "preferred_contact_method": preferred_contact_method,
                "route": "tier2"
            }
        
    except Exception as e:
        logger.error(f"Error in Tier 2 handler: {str(e)}", exc_info=True)
        return {
            "messages": [AIMessage(content=f"I apologize, but I'm having trouble processing your request. Please try contacting {business_name} directly at {business_email if business_email else 'their listed contact'}.")],
            "email_sent": False,
            "route": "tier2"
        }

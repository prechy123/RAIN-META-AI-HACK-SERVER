"""
Tier 2 Handler - Human Support Requests
Collects user contact info and sends email to business owner
"""
import logging
from langchain_core.messages import AIMessage
from agent.llm import get_llm
from agent.email_service import send_support_email
from agent.graph_builder.agent_state import AgentState
from agent.agent_utils import format_chat_history, get_last_user_message

logger = logging.getLogger("tier2")


async def Tier2(state: AgentState) -> dict:
    """
    Handle Tier 2 queries (human support requests).
    Collects user email and phone, then sends email to business owner.
    Returns dict to update state.
    """
    try:
        # Extract state variables
        user_email = state.get("user_email")
        user_phone = state.get("user_phone")
        business_name = state.get("business_name", "this business")
        business_email = state.get("business_email")
        
        # Check if we have user contact info
        if not user_email:
            # Ask for email
            return {
                "messages": [AIMessage(content="I'd be happy to connect you with the business owner! To help them reach you, could you please provide your email address?")],
                "needs_contact_info": True,
                "email_sent": False,
                "route": "tier2"
            }
            
        if not user_phone:
            # Ask for phone
            return {
                "messages": [AIMessage(content="Great! And could you also provide your phone number so the business owner can contact you?")],
                "needs_contact_info": True,
                "email_sent": False,
                "route": "tier2"
            }
        
        # We have all contact info - generate conversation summary
        logger.info(f"Generating conversation summary for {business_name}")
        
        # Build conversation summary using chat history
        conversation_text = format_chat_history(state["messages"])
        
        # Use LLM to create a brief summary
        llm = get_llm()
        
        summary_prompt = f"""Summarize the following customer conversation in 2-3 sentences.
Focus on what the customer needs and key details discussed.

CONVERSATION:
{conversation_text}

BRIEF SUMMARY:"""
        
        summary_response = await llm.ainvoke(summary_prompt)
        conversation_summary = summary_response.content.strip()
        
        # Extract support request (last user message)
        support_request = get_last_user_message(state["messages"])
        
        # Send email to business owner
        email_sent = await send_support_email(
            business_name=business_name,
            business_email=business_email,
            user_email=user_email,
            user_phone=user_phone,
            conversation_summary=conversation_summary,
            support_request=support_request
        )
        
        # Generate response message
        if email_sent:
            response_message = f"""Perfect! I've sent your request to {business_name}. 

They will contact you at:
📧 Email: {user_email}
📞 Phone: {user_phone}

The business owner has received a summary of our conversation and will get back to you soon. Is there anything else I can help you with?"""
        else:
            response_message = f"""I apologize, but there was an issue sending your request. 

You can contact {business_name} directly at:
📧 {business_email}

Please mention your contact details:
📧 Your Email: {user_email}
📞 Your Phone: {user_phone}

Is there anything else I can help you with?"""
        
        logger.info(f"Tier 2 complete - Email sent: {email_sent}")
        
        # Return dict with updates
        return {
            "messages": [AIMessage(content=response_message)],
            "needs_contact_info": False,
            "email_sent": email_sent,
            "route": "tier2"
        }
        
    except Exception as e:
        logger.error(f"Error in Tier 2 handler: {str(e)}", exc_info=True)
        return {
            "messages": [AIMessage(content="I'm having trouble processing your request right now. Please try contacting the business directly.")],
            "needs_contact_info": False,
            "email_sent": False,
            "route": "tier2"
        }

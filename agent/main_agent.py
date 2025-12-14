"""
Main agent entry point - invokes the compiled LangGraph agent
"""
import logging
from typing import Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage
from agent.graph_builder.compiled_agent import build_agent_graph
from config.database import business_collection

logger = logging.getLogger("main_agent")


async def get_business_info(business_id: str) -> Dict[str, str]:
    """
    Fetch business name and email from MongoDB.
    """
    try:
        business = business_collection.find_one({"business_id": business_id})
        
        if not business:
            logger.warning(f"Business {business_id} not found in database")
            return {
                "business_name": "this business",
                "business_email": "support@example.com"
            }
        
        return {
            "business_name": business.get("businessName"),
            "business_email": business.get("email")
        }
        
    except Exception as e:
        logger.error(f"Error fetching business info: {str(e)}")
        return {
            "business_name": "this business",
            "business_email": "support@example.com"
        }


async def main_agent(
    query: str,
    business_id: str,
    thread_id: str = "default",
    user_email: Optional[str] = None,
    user_phone: Optional[str] = None,
    business_name: Optional[str] = None,
    business_email: Optional[str] = None
) -> Dict[str, Any]:    
    """
    Invoke the compiled LangGraph agent.
    
    Args:
        query: User's message
        business_id: Business ID (required)
        thread_id: Conversation thread ID (unique per user session)
        user_email: User's email (optional, for Tier 2)
        user_phone: User's phone (optional, for Tier 2)
        business_name: Business name (optional, fetched from DB if not provided)
        business_email: Business email (optional, fetched from DB if not provided)
        
    Returns:
        {
            "answer": "AI response",
            "route": "tier1" | "tier2" | "conversation",
            "email_sent": bool,
            "business_name": str,
            "business_email": str,
            "user_email": str | None,
            "user_phone": str | None
        }
    """
    try:
        
        logger.info(f"Processing query for business {business_id}, thread {thread_id}")
        
        # Fetch business info if not provided
        if not business_name or not business_email:
            logger.info(f"Fetching business info for {business_id}")
            business_info = await get_business_info(business_id)
            business_name = business_name or business_info["business_name"]
            business_email = business_email or business_info["business_email"]
        
        # Prepare input state
        input_state = {
            "messages": [HumanMessage(content=query)],
            "business_id": business_id,
            "business_name": business_name,
            "business_email": business_email,
            "user_email": user_email,
            "user_phone": user_phone,
            "route": None,
            "email_sent": False
        }
        
        # Build/get the compiled agent
        compiled_agent = await build_agent_graph()
        
        # Invoke agent with thread-based memory
        config = {"configurable": {"thread_id": thread_id}}
        result = await compiled_agent.ainvoke(input_state, config)
        
        # Extract response
        last_message = result["messages"][-1]
        
        # Handle LangChain message objects
        if isinstance(last_message, AIMessage):
            answer = last_message.content
        elif isinstance(last_message, dict):
            answer = last_message.get("content", "")
        else:
            answer = str(last_message)
        
        response = {
            "answer": answer,
            "route": result.get("route"),
            "email_sent": result.get("email_sent", False),
            "business_name": business_name,
            "business_email": business_email,
            "user_email": result.get("user_email"),
            "user_phone": result.get("user_phone")
        }
        
        logger.info(f"Response generated - Route: {response['route']}")
        return response
        
    except Exception as e:
        logger.error(f"Error invoking agent: {str(e)}", exc_info=True)
        return {
            "answer": "I'm having trouble processing your request. Please try again.",
            "route": "error",
            "email_sent": False,
            "business_name": business_name or "this business",
            "business_email": business_email,
            "user_email": None,
            "user_phone": None
        }

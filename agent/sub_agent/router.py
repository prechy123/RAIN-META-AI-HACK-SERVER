"""
Router/Supervisor - Classifies user queries and routes to appropriate handler
"""
import logging
from agent.graph_builder.agent_state import AgentState
from agent.llm import get_llm
from agent.agent_utils import get_last_user_message

logger = logging.getLogger("router")


async def route_query(state: AgentState) -> dict:
    """
    Classify/Route user query to appropriate handler.
    This is used as a GRAPH NODE, so it returns a dict to update state.
    
    Returns:
        dict with "route" key set to "tier1", "tier2", or "conversation"
    """
    llm = get_llm()
    
    # Get last user message
    user_query = get_last_user_message(state["messages"])
    
    if not user_query:
        return {"route": "conversation"}
    
    routing_prompt = f"""You are a query router for a business chatbot.

Classify the user query into ONE of these categories:

1. **tier1** - Questions about business info (hours, location, services, prices, menu, FAQs)
2. **tier2** - Requests needing human help (reservations, orders, complaints, custom requests)
3. **conversation** - General greetings, small talk, unclear requests

User Query: "{user_query}"

Respond with ONLY ONE WORD: tier1, tier2, or conversation
"""
    
    try:
        response = await llm.ainvoke(routing_prompt)
        route = response.content.strip().lower()
        
        # Validate route
        if route not in ["tier1", "tier2", "conversation"]:
            logger.warning(f"Invalid route '{route}', defaulting to conversation")
            route = "conversation"
        
        logger.info(f"Routed to: {route}")
        
        # Return dict to update state
        return {"route": route}
        
    except Exception as e:
        logger.error(f"Routing error: {str(e)}")
        return {"route": "conversation"}

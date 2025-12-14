"""
Conversation Agent - Handles general chat and greetings
"""
import logging
from langchain_core.messages import AIMessage
from agent.graph_builder.agent_state import AgentState
from agent.llm import get_llm
from agent.agent_utils import format_chat_history, get_last_user_message

logger = logging.getLogger("conversation_agent")


async def conversation_agent(state: AgentState) -> dict:
    """
    Handle general conversation and greetings.
    Returns dict to update state.
    """
    llm = get_llm()
    
    # Get conversation context
    user_query = get_last_user_message(state["messages"])
    chat_history = format_chat_history(state["messages"][:-1])  # Exclude current message
    business_name = state.get("business_name", "this business")
    
    conversation_prompt = f"""You are SharpChatAI, a helpful and friendly customer care agent for {business_name}.

**YOUR PERSONALITY:**
- Warm, professional, and approachable
- Patient and understanding
- Proactive in offering help
- Clear and concise in communication

**CONVERSATION HISTORY:**
{chat_history}

**USER MESSAGE:** {user_query}

**YOUR TASK:**
- Respond naturally and helpfully
- If the user asks about business info (hours, prices, etc.), suggest they ask specific questions
- If they need help with reservations/orders, offer to connect them with the business owner
- Keep responses friendly and concise

**RESPONSE:**"""
    
    try:
        response = await llm.ainvoke(conversation_prompt)
        bot_response = response.content.strip()
        
        logger.info(f"Generated conversation response")
        
        # Return dict with AIMessage object
        return {
            "messages": [AIMessage(content=bot_response)]
        }
        
    except Exception as e:
        logger.error(f"Conversation error: {str(e)}")
        return {    
            "messages": [AIMessage(content="I'm having trouble right now. How can I help you with your inquiry?")]
        }
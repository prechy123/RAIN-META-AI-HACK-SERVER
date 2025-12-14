"""
Utility functions for agent operations
"""
import logging
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

logger = logging.getLogger("agent_utils")


def format_chat_history(messages: list) -> str:
    """
    Format chat history for inclusion in prompts.
    
    Args:
        messages: List of LangChain message objects (HumanMessage, AIMessage, etc.)
        
    Returns:
        Formatted string of conversation history
    """
    if not messages:
        return "No previous conversation."
    
    formatted = []
    # Only last 6 messages (3 exchanges)
    for msg in messages[-6:]:
        # Handle LangChain message objects
        if isinstance(msg, HumanMessage):
            content = msg.content if hasattr(msg, 'content') else ""
            formatted.append(f"User: {content}")
        elif isinstance(msg, AIMessage):
            content = msg.content if hasattr(msg, 'content') else ""
            formatted.append(f"Assistant: {content}")
        # Fallback for dict-like messages (backward compatibility)
        elif isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user" or role == "human":
                formatted.append(f"User: {content}")
            else:
                formatted.append(f"Assistant: {content}")
    
    return "\n".join(formatted)


def get_last_user_message(messages: list) -> str:
    """
    Extract the last user message from conversation history.
    
    Args:
        messages: List of LangChain message objects or dicts
        
    Returns:
        Last user message content
    """
    if not messages:
        return ""
    
    # Find last user message
    for msg in reversed(messages):
        # Handle LangChain HumanMessage objects
        if isinstance(msg, HumanMessage):
            return msg.content if hasattr(msg, 'content') else ""
        # Fallback for dict-like messages (backward compatibility)
        elif isinstance(msg, dict) and msg.get("role") in ["user", "human"]:
            return msg.get("content", "")
    
    return ""

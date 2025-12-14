from typing import TypedDict, List, Annotated, Optional
from langgraph.graph.message import add_messages


# Define state
class AgentState(TypedDict):
    """State for the agent graph"""
    # Input
    messages: Annotated[List, add_messages]  # Conversation history
    business_id: str
    business_name: str
    business_email: str
    
    # User contact info (for Tier 2)
    user_email: Optional[str]
    user_phone: Optional[str]
    preferred_contact_method: Optional[str]  # "email", "phone", or "both"
    
    # Routing
    route: Optional[str]  # "tier1", "tier2", or "conversation"
    
    # Tier 2 state
    email_sent: bool

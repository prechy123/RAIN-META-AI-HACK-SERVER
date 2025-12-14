"""
LangGraph compiled agent with state management and memory
"""
import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from agent.graph_builder.agent_state import AgentState
from agent.sub_agent.conversation_agent import conversation_agent
from agent.sub_agent.tier1 import Tier1
from agent.sub_agent.tier2 import Tier2
from agent.sub_agent.router import route_query
from config.conf import settings

logger = logging.getLogger("compiled_agent")


_checkpointer = None
_connection_pool = None
compiled_agent = None
db_initialized = False


async def get_checkpointer():
    """Get or create a PostgreSQL checkpointer with connection pooling."""
    global _checkpointer, _connection_pool, db_initialized
    
    # Return existing instance if already initialized
    if db_initialized and _checkpointer is not None:
        return _checkpointer
    
    db_url = settings.POSTGRES_DB_URL
    
    if not db_url:
        logger.warning("⚠️ POSTGRES_DB_URL not found. Running without memory...")
        return None
    
    try:
        logger.info("Initializing database connection pool...")
        
        # Create connection pool
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
            "row_factory": dict_row
        }
        
        _connection_pool = AsyncConnectionPool(
            conninfo=db_url,
            max_size=20,
            kwargs=connection_kwargs,
            open=False
        )
        
        await _connection_pool.open()
        logger.info("✅ Database connection pool established")
        
        # Initialize checkpointer
        _checkpointer = AsyncPostgresSaver(conn=_connection_pool)
        await _checkpointer.setup()
        
        # Mark DB as initialized
        db_initialized = True
        logger.info("✅ Checkpointer setup completed")
        
        return _checkpointer
        
    except Exception as e:
        logger.error(f"❌ Error setting up checkpointer: {e}")
        await close_checkpointer()
        raise e



# Build graph
async def build_agent_graph():
    """Build and compile the agent graph"""
    try:
        
        global compiled_agent
        
        # Return cached agent if already compiled
        if compiled_agent is not None:
            return compiled_agent
        
        # Initialize checkpointer first
        checkpointer = await get_checkpointer()
        
        # Define should_continue function for routing
        def should_continue(state: AgentState) -> str:
            """
            Routing function that reads the route from state.
            Used as conditional edge function.
            """
            route = state.get("route", "conversation")
            # Map route to node names
            if route == "tier1":
                return "Tier1"
            elif route == "tier2":
                return "Tier2"
            else:
                return "conversation_agent"
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", route_query)
        workflow.add_node("Tier1", Tier1)
        workflow.add_node("Tier2", Tier2)
        workflow.add_node("conversation_agent", conversation_agent)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            should_continue,
            {
                "Tier1": "Tier1",
                "Tier2": "Tier2",
                "conversation_agent": "conversation_agent"
            }
        )

        # All handlers end the conversation
        workflow.add_edge("Tier1", END)
        workflow.add_edge("Tier2", END)
        workflow.add_edge("conversation_agent", END)

        # Compile graph with memory
        compiled_agent = workflow.compile(checkpointer=checkpointer)
        
        logger.info("Agent graph compiled successfully")
        return compiled_agent
        
    except Exception as e:
        logger.error(f"Failed to build agent graph: {str(e)}")
        raise



async def close_checkpointer():
    """Close the database connection pool and cleanup resources."""
    global _checkpointer, _connection_pool, compiled_agent, db_initialized
    
    try:
        if _connection_pool:
            await _connection_pool.close()
            logger.info("✅ Database connection pool closed")
    except Exception as e:
        logger.error(f"❌ Error closing connection pool: {e}")
    finally:
        _checkpointer = None
        _connection_pool = None
        compiled_agent = None
        db_initialized = False

"""
Tier 1 Handler - FAQ Queries
Uses Pinecone retrieval to answer business-related questions
"""
import logging
from langchain_core.messages import AIMessage
from agent.retrieval import query_pinecone
from agent.llm import get_llm
from agent.graph_builder.agent_state import AgentState
from agent.agent_utils import format_chat_history, get_last_user_message

logger = logging.getLogger("tier1")


async def Tier1(state: AgentState) -> dict:
    """
    Handle FAQ queries using Pinecone retrieval + LLM.
    Returns dict to update state.
    """
    try:
        # Extract from state
        business_id = state.get("business_id")
        business_name = state.get("business_name", "this business")
        user_message = get_last_user_message(state["messages"])
        
        # Step 1: Retrieve relevant business info from Pinecone
        logger.info(f"Querying Pinecone for business {business_id}")
        results = query_pinecone(
            query_text=user_message,
            business_id=business_id,
            top_k=3
        )
        
        if not results:
            return {
                "messages": [AIMessage(content="I couldn't find any information about that. Could you please rephrase your question?")]
            }
        
        # Step 2: Extract context from results
        context_parts = []
        sources = []
        
        for idx, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            text = metadata.get('text', '')
            score = result.get('score', 0.0)
            
            if text:
                context_parts.append(f"[Source {idx}]:\n{text}\n")
                sources.append({
                    "business_name": metadata.get('business_name', 'N/A'),
                    "category": metadata.get('category', 'N/A'),
                    "score": score
                })
        
        context = "\n".join(context_parts)
        
        # Step 3: Build conversation context using utility
        chat_history = format_chat_history(state["messages"][:-1])  # Exclude current message
        
        # Step 4: Generate answer using LLM
        llm = get_llm()
        
        prompt = f"""You are a helpful business assistant for {business_name}.

Use the following business information to answer the user's question accurately and naturally.

BUSINESS INFORMATION:
{context}

CONVERSATION HISTORY:
{chat_history}

USER QUESTION: {user_message}

INSTRUCTIONS:
- Answer based ONLY on the provided business information
- Be friendly, concise, and helpful
- If the information isn't in the context, say "I don't have that information, but I can help you contact the business owner"
- Include specific details like prices (₦), hours, location when relevant
- Don't make up information

ANSWER:"""
        
        response = await llm.ainvoke(prompt)
        answer = response.content.strip()
        
        # Calculate confidence based on retrieval scores
        avg_score = sum(s['score'] for s in sources) / len(sources) if sources else 0.0
        confidence = min(avg_score, 1.0)
        
        logger.info(f"Generated FAQ answer (confidence: {confidence:.2f})")
        
        # Return dict with AIMessage
        return {
            "messages": [AIMessage(content=answer)]
        }
        
    except Exception as e:
        logger.error(f"Error in Tier 1 handler: {str(e)}", exc_info=True)
        return {
            "messages": [AIMessage(content="I'm having trouble processing your question right now. Please try again.")]
        }

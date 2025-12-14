import logging
from typing import List, Dict, Any, Optional
from vector_db.vectors import VectorPipeline

logger= logging.getLogger("retrieval_tool")

# Query Pinecone
def query_pinecone(
    query_text: str,
    business_id: str,  # ← Required! User's business ID
    pipeline: Optional[VectorPipeline] = None,
    top_k: int = 5,
    namespace: str = ""
) -> List[Dict[str, Any]]:
    """
    Query Pinecone for business information.
    
    Args:
        query_text: User's question
        business_id: The business ID to query
        pipeline: VectorPipeline instance
        top_k: Number of results to return
        namespace: Pinecone namespace
        
    Returns:
        List of matching results with scores and metadata
        
    Example:
        # Chatbot query - ONLY user's business
        results = query_similar_businesses(
            query_text="What are your opening hours?",
            business_id="BUS-0001"  # User's registered business
        )
    """
    try:
        if pipeline is None:
            pipeline = VectorPipeline()
        
        # Generate query embedding
        query_embedding = pipeline.embeddings.embed_query(query_text)
        
        # Filter by business_id
        filter_dict = {"business_id": {"$eq": business_id}}
        logger.info(f"🔒 Querying business_id: {business_id}")
        
        # Query Pinecone
        results = pipeline.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
            filter=filter_dict
        )
        
        # Format results
        matches = []
        for match in results.get('matches', []):
            matches.append({
                'id': match['id'],
                'score': match['score'],
                'metadata': match.get('metadata', {})
            })
        
        logger.info(f"✅ Found {len(matches)} results for business {business_id}")
        
        return matches
        
    except Exception as e:
        logger.error(f"❌ Failed to query business {business_id}: {str(e)}")
        return []

"""
Knowledge Base Management Routes
Endpoints for managing the Pinecone vector database
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from vector_db.kb_toolkit import (
    embed_all_documents,
    VectorPipeline
)
from config.conf import settings
from models.kbase import (
    EmbedRequest,
    EmbedResponse,
    DeleteResponse
)
logger = logging.getLogger("kb_routes")

router = APIRouter()


@router.post("/embed", response_model=EmbedResponse)
async def embed_documents(request: EmbedRequest):
    """
    Embed business documents to Pinecone vector database.
    """
    try:
        logger.info(f"Starting embed operation - business_id: {request.business_id}, category: {request.category}")
        
        # Call embed_all_documents with filters
        result = embed_all_documents(
            limit=request.limit,
            category=request.category,
            chunk_text_content=True,
            batch_size=100,
            namespace=""
        )
        
        if result.get("status") == "success":
            return EmbedResponse(
                status="success",
                message=f"Successfully embedded {result.get('total_businesses', 0)} businesses",
                total_businesses=result.get("total_businesses", 0),
                total_vectors=result.get("total_vectors", 0),
                changed_businesses=result.get("changed_businesses", 0),
                skipped_businesses=result.get("skipped_businesses", 0)
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error occurred")
            )
        
    except Exception as e:
        logger.error(f"Error in embed endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/business/{business_id}", response_model=DeleteResponse)
async def delete_business(business_id: str):
    """
    Delete a specific business from the knowledge base.
    
    **Deletes:**
    - All vectors associated with the business_id
    - Removes from Pinecone index
    
    Args:
        business_id: Business ID to delete (e.g., "BUS-0001")
        
    Example:
        ```
        DELETE /kb/business/BUS-0001
        ```
    """
    try:
        logger.info(f"Deleting business {business_id} from knowledge base")
        
        # Initialize pipeline
        pipeline = VectorPipeline(
            index_name=settings.KB_INDEX,
            embedding_model=settings.HUGGINGFACE_EMBED_MODEL,
            dimension=384
        )
        
        # Delete vectors with matching business_id
        delete_response = pipeline.index.delete(
            filter={"business_id": business_id},
            namespace=""
        )
        
        logger.info(f"Successfully deleted business {business_id}")
        
        return DeleteResponse(
            status="success",
            message=f"Successfully deleted business {business_id}",
            deleted_count=1  # Pinecone doesn't return count, assume 1 business
        )
        
    except Exception as e:
        logger.error(f"Error deleting business: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/index", response_model=DeleteResponse)
async def delete_index():
    """
    Delete the entire Pinecone index.
    
    **WARNING:** This will delete ALL business data from the knowledge base!
    
    **Use cases:**
    - Complete reset of knowledge base
    - Before re-indexing all data
    - Testing/development
    
    Example:
        ```
        DELETE /kb/index
        ```
    """
    try:
        logger.warning("Deleting entire Pinecone index!")
        
        # Initialize pipeline
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Delete index
        pc.delete_index(settings.KB_INDEX)
        
        logger.info(f"Successfully deleted index {settings.KB_INDEX}")
        
        return DeleteResponse(
            status="success",
            message=f"Successfully deleted index '{settings.KB_INDEX}'",
            deleted_count=0  # Unknown count
        )
        
    except Exception as e:
        logger.error(f"Error deleting index: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """
    Get knowledge base statistics.
    
    **Returns:**
    - Total vector count
    - Index dimension
    - Namespace info
    
    Example:
        ```
        GET /kb/stats
        ```
    """
    try:
        # Initialize pipeline
        pipeline = VectorPipeline(
            index_name=settings.KB_INDEX,
            embedding_model=settings.HUGGINGFACE_EMBED_MODEL,
            dimension=384
        )
        
        # Get index stats
        stats = pipeline.index.describe_index_stats()
        
        return {
            "status": "success",
            "index_name": settings.KB_INDEX,
            "total_vectors": stats.get("total_vector_count", 0),
            "dimension": stats.get("dimension", 384),
            "namespaces": stats.get("namespaces", {})
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


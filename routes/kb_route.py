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
    EmbedSingleBusinessRequest,
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
        logger.info(f"Starting embed for all data in the MongoDB Business Collection")
        
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


@router.post("/embed/business", response_model=EmbedResponse)
async def embed_single_business(request: EmbedSingleBusinessRequest):
    """
    Embed a single business to Pinecone vector database.
    
    **Use this to:**
    - Update a specific business after changes
    - Add a newly created business to the knowledge base
    - Re-sync a single business without affecting others
    
    Args:
        business_id: The specific business ID to embed (e.g., "BUS-0001")
        
    Example:
        ```json
        {
          "business_id": "BUS-0001"
        }
        ```
    """
    try:
        logger.info(f"Embedding single business: {request.business_id}")
        
        # Fetch the specific business from MongoDB
        from config.database import business_collection
        business = business_collection.find_one({"business_id": request.business_id})
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business {request.business_id} not found in database"
            )
        
        # Initialize pipeline
        pipeline = VectorPipeline()
        
        # Create vector records for this business
        from vector_db.kb_toolkit import create_vector_records, upsert_to_pinecone, check_if_business_changed
        
        # Check if business has changed
        namespace = ""
        has_changed = check_if_business_changed(business, pipeline, namespace)
        
        if not has_changed:
            logger.info(f"Business {request.business_id} is already up-to-date")
            return EmbedResponse(
                status="success",
                message=f"Business {request.business_id} is already up-to-date",
                total_businesses=1,
                total_vectors=0,
                changed_businesses=0,
                skipped_businesses=1
            )
        
        # Create and upsert vectors
        records = create_vector_records(business, chunk_text_content=True)
        
        if records:
            stats = upsert_to_pinecone(pipeline, records, batch_size=100, namespace=namespace)
            
            return EmbedResponse(
                status="success",
                message=f"Successfully embedded business {request.business_id}",
                total_businesses=1,
                total_vectors=len(records),
                changed_businesses=1,
                skipped_businesses=0
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create vector records for business {request.business_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error embedding single business: {str(e)}", exc_info=True)
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
        
        # Initialize pipeline (no parameters needed - reads from settings)
        pipeline = VectorPipeline()
        
        # Delete vectors with matching business_id
        delete_response = pipeline.index.delete(
            filter={"business_id": business_id},
            namespace=""
        )
        
        logger.info(f"Successfully deleted business {business_id}")
        
        return DeleteResponse(
            status="success",
            message=f"Successfully deleted business {business_id}"
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
        # Initialize pipeline (no parameters needed - reads from settings)
        pipeline = VectorPipeline()
        
        # Get index stats (returns Pinecone object)
        stats = pipeline.index.describe_index_stats()
        
        # Convert to dict for JSON serialization
        stats_dict = stats.to_dict()
        
        return {
            "status": "success",
            "index_name": settings.KB_INDEX,
            "total_vectors": stats_dict.get("total_vector_count", 0),
            "dimension": stats_dict.get("dimension", 384),
            "namespaces": stats_dict.get("namespaces", {})
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.database import business_collection
from vector_db.vectors import VectorPipeline

logger = logging.getLogger("kb_toolkit")


def fetch_businesses_from_mongo(
    limit: Optional[int] = None,
    business_id: Optional[str] = None,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch business data from MongoDB.
    
    Args:
        limit: Maximum number of businesses to fetch
        business_id: Specific business ID to fetch
        category: Filter by business category
        
    Returns:
        List of business documents
    """
    try:
        query = {}
        
        if business_id:
            query["business_id"] = business_id
        
        if category:
            query["businessCategory"] = category
        
        logger.info(f"Fetching businesses from MongoDB with query: {query}")
        
        cursor = business_collection.find(query)
        
        if limit:
            cursor = cursor.limit(limit)
        
        businesses = list(cursor)
        logger.info(f"SUCCESS: Fetched {len(businesses)} businesses from MongoDB")
        
        return businesses
        
    except Exception as e:
        logger.error(f"ERROR: Failed to fetch businesses from MongoDB: {str(e)}")
        raise


def generate_business_doc_id(business: Dict[str, Any]) -> str:
    """
    Compute a hash of the business data to detect changes.
    
    Args:
        business: Business document from MongoDB
        
    Returns:
        SHA256 hash string of the business content
    """
    # Extract only the fields that affect the embedding
    # (exclude _id, email, password, timestamps, etc.)
    relevant_fields = {
        'business_id': business.get('business_id'),
        'businessName': business.get('businessName'),
        'businessDescription': business.get('businessDescription'),
        'businessAddress': business.get('businessAddress'),
        'businessPhone': business.get('businessPhone'),
        'businessEmailAddress': business.get('businessEmailAddress'),
        'businessCategory': business.get('businessCategory'),
        'businessOpenHours': business.get('businessOpenHours'),
        'businessOpenDays': business.get('businessOpenDays'),
        'businessWebsite': business.get('businessWebsite'),
        'extra_information': business.get('extra_information'),
        'faqs': business.get('faqs', []),
        'items': business.get('items', [])
    }
    
    # Convert to JSON string (sorted for consistency)
    import json
    content_str = json.dumps(relevant_fields, sort_keys=True, default=str)
    
    # Compute SHA256 hash
    hash_obj = hashlib.sha256(content_str.encode('utf-8'))
    return hash_obj.hexdigest()



def process_business_to_text(business: Dict[str, Any]) -> str:
    """
    Convert business document to a text representation for embedding.
    
    Args:
        business: Business document from MongoDB
        
    Returns:
        Formatted text string
    """
    text_parts = []
    
    # Basic information
    text_parts.append(f"Business Name: {business.get('businessName', 'N/A')}")
    text_parts.append(f"Category: {business.get('businessCategory', 'N/A')}")
    text_parts.append(f"Description: {business.get('businessDescription', 'N/A')}")
    
    # Contact information
    text_parts.append(f"Address: {business.get('businessAddress', 'N/A')}")
    text_parts.append(f"Phone: {business.get('businessPhone', 'N/A')}")
    
    # Only use businessEmailAddress (public contact)
    if business.get('businessEmailAddress'):
        text_parts.append(f"Email: {business['businessEmailAddress']}")
    
    if business.get('businessWebsite'):
        text_parts.append(f"Website: {business['businessWebsite']}")
    
    # Operating hours
    if business.get('businessOpenHours'):
        text_parts.append(f"Open Hours: {business['businessOpenHours']}")
    
    if business.get('businessOpenDays'):
        text_parts.append(f"Open Days: {business['businessOpenDays']}")
    
    # Extra information
    if business.get('extra_information'):
        text_parts.append(f"Additional Info: {business['extra_information']}")
    
    # FAQs
    faqs = business.get('faqs', [])
    if faqs:
        text_parts.append("\nFrequently Asked Questions:")
        for faq in faqs:
            text_parts.append(f"Q: {faq.get('question', '')}")
            text_parts.append(f"A: {faq.get('answer', '')}")
    
    # Items/Products
    items = business.get('items', [])
    if items:
        text_parts.append("\nProducts/Services:")
        for item in items:
            # Use Nigerian Naira symbol (₦) for prices
            price = item.get('price', 0)
            item_text = f"- {item.get('name', 'N/A')} (₦{price:,.0f})"
            if item.get('description'):
                item_text += f": {item['description']}"
            text_parts.append(item_text)
    
    return "\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = 750, overlap: int = 150) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks


def create_vector_records(
    business: Dict[str, Any],
    chunk_text_content: bool = True,
    chunk_size: int = 750,
    overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Create vector records from a business document.
    
    Args:
        business: Business document from MongoDB
        chunk_text_content: Whether to chunk the text into smaller pieces
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of records ready for embedding and upserting
    """
    business_text = process_business_to_text(business)
    business_id = business.get('business_id')
    
    # Compute hash of business content for change detection
    content_hash = generate_business_doc_id(business)
    
    records = []
    
    if chunk_text_content and len(business_text) > chunk_size:
        chunks = chunk_text(business_text, chunk_size, overlap)
        
    record = {
        'id': content_hash,
        'text': business_text,  # ← This is what gets embedded!
        'metadata': {
            'business_id': business_id,
            'business_name': business.get('businessName', 'N/A'),
            'category': business.get('businessCategory', 'N/A'),
            'business_email': business.get('businessEmailAddress', 'N/A'),
            'content_hash': content_hash,  # ADD THIS: Store hash for change detection
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    records.append(record)
    
    return records

    


def upsert_to_pinecone(
    pipeline: VectorPipeline,
    records: List[Dict[str, Any]],
    batch_size: int = 100,
    namespace: str = ""
) -> Dict[str, Any]:
    """
    Upsert vector records to Pinecone.
    
    Args:
        pipeline: VectorPipeline instance
        records: List of records with 'id', 'text', and 'metadata'
        batch_size: Number of records to upsert at once
        namespace: Pinecone namespace to use
        
    Returns:
        Dictionary with upsert statistics
    """
    try:
        total_records = len(records)
        logger.info(f"Starting upsert of {total_records} records to Pinecone")
        
        upserted_count = 0
        failed_count = 0
        
        for i in range(0, total_records, batch_size):
            batch = records[i:i + batch_size]
            
            try:
                # Generate embeddings for the batch
                texts = [record['text'] for record in batch]
                embeddings = pipeline.embeddings.embed_documents(texts)
                
                # Prepare vectors for Pinecone
                vectors = []
                for record, embedding in zip(batch, embeddings):
                    # Include 'text' in metadata so it's stored in Pinecone
                    metadata_with_text = {
                        **record['metadata'],
                        'text': record['text']  # ← Store the actual content!
                    }
                    vectors.append({
                        'id': record['id'],
                        'values': embedding,
                        'metadata': metadata_with_text
                    })
                
                # Upsert to Pinecone
                pipeline.index.upsert(vectors=vectors, namespace=namespace)
                upserted_count += len(vectors)
                
                logger.info(f"SUCCESS: Upserted batch {i//batch_size + 1}: {len(vectors)} vectors")
                
            except Exception as e:
                logger.error(f"ERROR: Failed to upsert batch {i//batch_size + 1}: {str(e)}")
                failed_count += len(batch)
        
        stats = {
            'total_records': total_records,
            'upserted': upserted_count,
            'failed': failed_count,
            'success_rate': (upserted_count / total_records * 100) if total_records > 0 else 0
        }
        
        logger.info(f"SUCCESS: Upsert complete: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"ERROR: Failed to upsert to Pinecone: {str(e)}")
        raise


def check_if_business_changed(
    business: Dict[str, Any],
    pipeline: VectorPipeline,
    namespace: str = ""
) -> bool:
    """
    Check if business content has changed by comparing hashes.
    
    Args:
        business: Business document from MongoDB
        pipeline: VectorPipeline instance
        namespace: Pinecone namespace
        
    Returns:
        True if business changed or doesn't exist (needs sync), False if unchanged (skip)
    """
    try:
        business_id = business.get('business_id')
        current_hash = generate_business_doc_id(business)
        
        # Query by metadata filter to get existing business
        dimension = len(pipeline.embeddings.embed_query("test"))
        
        results = pipeline.index.query(
            vector=[0] * dimension,  # Dummy vector
            filter={"business_id": {"$eq": business_id}},
            top_k=1,
            include_metadata=True,
            namespace=namespace
        )
        
        matches = results.get('matches', [])
        
        if not matches:
            # Business doesn't exist in Pinecone
            logger.info(f"NEW: Business {business_id} not found in index, will insert")
            return True
        
        # Business exists - check if content changed
        existing_hash = matches[0].get('metadata', {}).get('content_hash')
        
        if existing_hash == current_hash:
            # Content hasn't changed
            logger.info(f"SKIP: Business {business_id} unchanged (hash match)")
            return False
        else:
            # Content has changed
            logger.info(f"UPDATE: Business {business_id} content changed (hash mismatch)")
            return True
            
    except Exception as e:
        logger.error(f"ERROR: Error checking if business changed: {str(e)}")
        # On error, assume changed to be safe
        return True


def embed_all_documents(
    limit: Optional[int] = None,
    category: Optional[str] = None,
    chunk_text_content: bool = True,
    batch_size: int = 100,
    namespace: str = ""
) -> Dict[str, Any]:
    """
    Sync all businesses from MongoDB to Pinecone.
    
    Args:
        limit: Maximum number of businesses to sync
        category: Filter by category
        chunk_text_content: Whether to chunk the text
        batch_size: Batch size for Pinecone upserts
        namespace: Pinecone namespace
        
    Returns:
        Overall sync statistics
    """
    try:
        logger.info("Starting full sync from MongoDB to Pinecone")

        pipeline = VectorPipeline()
        
        # Fetch businesses
        businesses = fetch_businesses_from_mongo(limit=limit, category=category)
        
        if not businesses:
            logger.warning("WARNING: No businesses found in MongoDB")
            return {'status': 'no_data', 'total_businesses': 0}
        
        # Check for changes and create vector records only for changed businesses
        all_records = []
        skipped_count = 0
        changed_count = 0
        
        for business in businesses:
            # Check if business has changed
            if check_if_business_changed(business, pipeline, namespace):
                records = create_vector_records(business, chunk_text_content)
                all_records.extend(records)
                changed_count += 1
            else:
                skipped_count += 1
        
        # Upsert to Pinecone (only changed businesses)
        if all_records:
            stats = upsert_to_pinecone(pipeline, all_records, batch_size, namespace)
        else:
            logger.info("SUCCESS: All businesses are up-to-date, nothing to sync")
            stats = {'total_records': 0, 'upserted': 0, 'failed': 0, 'success_rate': 100.0}
        
        # Get final index stats
        index_stats = pipeline.get_index_stats()
        
        return {
            'status': 'success',
            'total_businesses': len(businesses),
            'changed_businesses': changed_count,
            'skipped_businesses': skipped_count,
            'total_vectors': len(all_records),
            'upsert_stats': stats,
            'index_stats': index_stats
        }
        
    except Exception as e:
        logger.error(f"ERROR: Failed to sync all businesses: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


def process_and_embed_business(business_id: str) -> Dict[str, Any]:
    """
    Process a single business for embedding: fetch, check changes, and upsert if needed.
    Can be used by signup/update endpoints directly.
    """
    try:
        logger.info(f"Processing embedding for business: {business_id}")
        
        # Fetch business
        business = business_collection.find_one({"business_id": business_id})
        if not business:
            return {
                "status": "error",
                "message": f"Business {business_id} not found in database",
                "error": True
            }
        
        # Initialize pipeline
        pipeline = VectorPipeline()
        namespace = ""
        
        # Check for changes
        has_changed = check_if_business_changed(business, pipeline, namespace)
        
        if not has_changed:
            logger.info(f"Business {business_id} is unchanged")
            return {
                "status": "success",
                "message": f"Business {business_id} is already up-to-date",
                "embedding_status": "skipped",
                "total_businesses": 1,
                "total_vectors": 0,
                "changed_businesses": 0,
                "skipped_businesses": 1
            }
            
        # Create and upsert vectors
        records = create_vector_records(business, chunk_text_content=True)
        
        if records:
            stats = upsert_to_pinecone(pipeline, records, batch_size=100, namespace=namespace)
            return {
                "status": "success",
                "message": f"Successfully embedded business {business_id}",
                "embedding_status": "embedded",
                "total_businesses": 1,
                "total_vectors": len(records),
                "changed_businesses": 1,
                "skipped_businesses": 0,
                "upsert_stats": stats
            }
        else:
            return {
                "status": "error", 
                "message": f"No content to embed for {business_id}",
                "error": True
            }
            
    except Exception as e:
        logger.error(f"Error embedding business {business_id}: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Embedding failed: {str(e)}",
            "error": True
        }



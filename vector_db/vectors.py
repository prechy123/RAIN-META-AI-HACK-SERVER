import logging
import hashlib
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from config.conf import settings
from vector_db.embedding import get_embeddings

logger = logging.getLogger("vector_pipeline")

class VectorPipeline:
    """Handles the data pipeline from MongoDB to Pinecone."""
    
    def __init__(self):
        """Initialize the vector pipeline with Pinecone and embeddings."""
        self.embeddings = get_embeddings()
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.KB_INDEX
        self._ensure_index_exists()
        
    def _ensure_index_exists(self):
        """Ensure Pinecone index exists, create if not."""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                # Get embedding dimension from the model
                test_embedding = self.embeddings.embed_query("test")
                dimension = len(test_embedding)
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=settings.PINECONE_CLOUD,
                        region=settings.PINECONE_REGION
                    )
                )
                logger.info(f"SUCCESS: Created index '{self.index_name}' with dimension {dimension}")
            else:
                logger.info(f"SUCCESS: Index '{self.index_name}' already exists")
                
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone index: {str(e)}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index."""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"❌ Failed to get index stats: {str(e)}")
            return {}

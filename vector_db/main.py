"""
Run this command to embed all document: python -m vector_db.main
"""

import logging
from vector_db.kb_toolkit import embed_all_documents


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vector_pipeline.log')
    ]
)

logger = logging.getLogger("main_vector_pipeline")


def main():
    """
    Sync all businesses data from MongoDB to Pinecone.
    """
    logger.info("STARTING FULL SYNC: MongoDB -> Pinecone")
    
    try:
        result= embed_all_documents()
    
        logger.info("\nPipeline Sync Completed")
        logger.info(f"Status: {result.get('status')}")
        logger.info(f"Total businesses processed: {result.get('total_businesses', 0)}")
        logger.info(f"Total vectors created: {result.get('total_vectors', 0)}")

    except Exception as e:
        logger.error(f"\n❌ Pipeline execution failed: {str(e)}", exc_info=True)
        raise

    
if __name__ == "__main__":
    main()

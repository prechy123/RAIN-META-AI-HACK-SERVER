from langchain_huggingface import HuggingFaceEmbeddings
import logging
from config.conf import settings

logger = logging.getLogger("embeddings")

def get_embeddings():
    """
    Get HuggingFace embedding model.
    """
    try:
        model_name = settings.HUGGINGFACE_EMBED_MODEL
        logger.info(f"Initializing HuggingFace embeddings...")
        
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # Use CPU (works everywhere)
            encode_kwargs={'normalize_embeddings': True}  # Better similarity search
        )
        
        return embeddings
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize HuggingFace embeddings: {str(e)}")
        raise RuntimeError(
            f"Failed to initialize embeddings. Error: {str(e)}\n"
        )

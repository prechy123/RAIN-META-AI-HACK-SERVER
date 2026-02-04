from langchain_cohere import CohereEmbeddings
from config.conf import settings

def get_embeddings():
    """
    Get Embeddings - Optimized for Cohere rate limits
    Using light model to reduce token usage and cost
    """
    embeddings = CohereEmbeddings(
        model="embed-english-light-v3.0", 
        cohere_api_key=settings.COHERE_API_KEY,
        max_retries=5,  
        request_timeout=120  
    )
    
    return embeddings



# from langchain_openai import OpenAIEmbeddings
# from config.conf import settings

# def get_embeddings():
#     """
#     Get Embeddings
#     """
    
#     embeddings = OpenAIEmbeddings(
#         model=settings.OPENAI_EMBEDDING_NAME,
#         openai_api_key=settings.OPENAI_API_KEY
#     )
    
#     return embeddings
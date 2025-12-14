from langchain_groq import ChatGroq
from config.conf import settings


def get_llm():
    """
    Initialize and return the LLM (Groq) instance.
    
    Returns:
        ChatGroq: Configured LLM instance
    """
    llm = ChatGroq(
        model=settings.LLAMA_MODEL,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
        api_key=settings.GROQ_API_KEY
    )
    return llm
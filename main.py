from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes.utils.auth import endpoint_auth
from agent.graph_builder.compiled_agent import close_checkpointer
from routes.business_routes import router as BusinessRouter
from routes.whatsapp_routes import router as WhatsAppRouter
from routes.chatbot_routes import router as ChatbotRouter
from routes.kb_route import router as KBRouter
import logging

# Configure logging to show INFO level and above
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:     %(name)s - %(message)s'
)

logger = logging.getLogger("fastapi_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup actions
    logger.info("Starting up FastAPI application...")
    yield
    # Shutdown actions
    logger.info("Shutting down FastAPI application...")
    try:
        await close_checkpointer()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")



app = FastAPI(
    title= "ShapChat API",
    description="AI-Powered Chatting platform for local SMEs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the SharpChat AI Chatbot API! Visit /docs for API documentation."
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SharpChat AI Chatbot"
    }


app.include_router(BusinessRouter, prefix="/business", tags=["Business"], dependencies=[Depends(endpoint_auth)])
app.include_router(WhatsAppRouter, prefix="/whatsapp", tags=["WhatsApp"], dependencies=[Depends(endpoint_auth)])
app.include_router(ChatbotRouter, prefix="/chatbot", tags=["Chatbot"], dependencies=[Depends(endpoint_auth)])
app.include_router(KBRouter, prefix="/kb", tags=["Knowledge Base"], dependencies=[Depends(endpoint_auth)])
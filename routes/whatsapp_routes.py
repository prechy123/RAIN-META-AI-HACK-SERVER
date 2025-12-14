from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.whatsapp import WhatsAppSession
from config.database import business_collection, session_collection
from schema.schemas import business_serial, business_list_serial
from datetime import datetime
from bson import ObjectId

router = APIRouter()

# POST - Start WhatsApp session
@router.post("/session/start")
async def start_session(whatsapp_number: str):
    try:
        session_dict = {
            "whatsapp_number": whatsapp_number,
            "business_id": None,
            "conversation_history": [],
            "active": True,
            "created_at": datetime.now()
        }
        result = session_collection.insert_one(session_dict)
        
        return JSONResponse(
            status_code=200,
            content={"session_id": str(result.inserted_id), "message": "Session started"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )

# POST - Search business in WhatsApp
@router.post("/search")
async def search_in_whatsapp(session_id: str, query: str):
    try:
        # Try to find by business_id first
        business = business_collection.find_one({"business_id": query})
        if business:
            return JSONResponse(
                status_code=200,
                content={"type": "exact", "business": business_serial(business)}
            )
        
        # Search by name
        businesses = business_collection.find({"name": {"$regex": query, "$options": "i"}})
        
        return JSONResponse(
            status_code=200,
            content={"type": "list", "businesses": business_list_serial(businesses)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )

# POST - Ask question about business (integrated with AI agent)
@router.post("/ask")
async def ask_question(session_id: str, business_id: str, question: str, thread_id: str):
    """
    Ask a question about a business using the AI agent.
    
    **Features:**
    - Tier 1 (FAQ): Answers from Pinecone knowledge base
    - Tier 2 (Support): Collects contact info and emails business owner
    - Conversation: General chat
    - Conversation history tracking
    """
    try:
        # Validate business exists
        business = business_collection.find_one({"business_id": business_id})
        if not business:
            return JSONResponse(
                status_code=404,
                content={"message": "Business not found", "error": True}
            )
        
        # Get session for conversation history
        session = session_collection.find_one({"_id": ObjectId(session_id)})
        if not session:
            return JSONResponse(
                status_code=404,
                content={"message": "Session not found", "error": True}
            )
        
        # Call main_agent with WhatsApp session
        from agent.main_agent import main_agent
        
        result = await main_agent(
            query=question,
            business_id=business_id,
            thread_id=thread_id,
            user_email=None,
            user_phone=None
        )
        
        answer = result.get("answer", "I'm having trouble processing your request.")
        route = result.get("route", "unknown")
        needs_contact_info = result.get("needs_contact_info", False)
        email_sent = result.get("email_sent", False)
        
        # Update session history
        session_collection.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$push": {
                    "conversation_history": {
                        "question": question,
                        "answer": answer,
                        "route": route,
                        "timestamp": datetime.now()
                    }
                },
                "$set": {
                    "business_id": business_id,  # Track current business
                    "last_activity": datetime.now()
                }
            }
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "answer": answer,
                "route": route,
                "needs_contact_info": needs_contact_info,
                "email_sent": email_sent
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )

# POST - End session
@router.post("/session/end")
async def end_session(session_id: str):
    try:
        result = session_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"active": False}}
        )
        
        if result.matched_count == 0:
            return JSONResponse(
                status_code=400,
                content={"message": "Session not found", "error": True}
            )
        
        return JSONResponse(
            status_code=200,
            content={"message": "Session ended"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )
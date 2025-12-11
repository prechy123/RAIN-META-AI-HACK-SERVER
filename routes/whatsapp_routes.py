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

# POST - Ask question about business (integrate with Llama here)
@router.post("/ask")
async def ask_question(session_id: str, business_id: str, question: str):
    try:
        business = business_collection.find_one({"business_id": business_id})
        if not business:
            return JSONResponse(
                status_code=400,
                content={"message": "Business not found", "error": True}
            )
        
        # TODO: Integrate with Llama AI here to generate response based on business data
        # For now, return a simple response
        response = f"This is information about {business['name']}"
        
        # Update session history
        session_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$push": {"conversation_history": {"question": question, "answer": response}}}
        )
        
        return JSONResponse(
            status_code=200,
            content={"answer": response}
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
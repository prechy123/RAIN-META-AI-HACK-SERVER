from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.business import Business, BusinessUpdate
from config.database import business_collection
from schema.schemas import business_serial, business_list_serial
from bson import ObjectId
from passlib.context import CryptContext
from vector_db.kb_toolkit import process_and_embed_business

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_business_id():
    """Generate unique business ID like BUS-0001"""
    last_business = business_collection.find_one(sort=[("business_id", -1)])
    if last_business and last_business.get("business_id"):
        last_num = int(last_business["business_id"].split("-")[1])
        return f"BUS-{str(last_num + 1).zfill(4)}"
    return "BUS-0001"

# POST - Business Signup


@router.post("/signup")
async def signup_business(business: Business):
    try:
        existing = business_collection.find_one({"email": business.email})
        if existing:
            return JSONResponse(
                status_code=400,
                content={"message": "Email already registered", "error": True}
            )

        business_dict = business.model_dump()
        password = str(business.password)
        business_dict["password"] = password
        business_dict["business_id"] = generate_business_id()
        business_dict["faqs"] = business_dict.get("faqs", [])
        business_dict["items"] = business_dict.get("items", [])

        result = business_collection.insert_one(business_dict)
        new_business = business_collection.find_one(
            {"_id": result.inserted_id})
            
        # Trigger embedding for the new business
        embedding_result = process_and_embed_business(new_business["business_id"])

        return JSONResponse(
            status_code=200,
            content={"message": "Business registered successfully",
                     "business": business_serial(new_business),
                     "embedding_result": embedding_result}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )


# POST - Business Login
@router.post("/login")
async def login_business(email: str, password: str):
    try:
        business = business_collection.find_one({"email": email})
        if not business or not password == business["password"]:
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid credentials", "error": True}
            )

        return JSONResponse(
            status_code=200,
            content={"message": "Login successful",
                     "business": business_serial(business)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )


# GET - Get business by ID
@router.get("/{business_id}")
async def get_business(business_id: str):
    try:
        business = business_collection.find_one({"business_id": business_id})
        if not business:
            return JSONResponse(
                status_code=400,
                content={"message": "Business not found", "error": True}
            )

        return JSONResponse(
            status_code=200,
            content=business_serial(business)
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )


# GET - Search businesses by name
@router.get("/search/{name}")
async def search_business(name: str):
    try:
        businesses = business_collection.find(
            {"name": {"$regex": name, "$options": "i"}})

        return JSONResponse(
            status_code=200,
            content={"businesses": business_list_serial(businesses)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )

# PUT - Update business information


@router.put("/{business_id}")
async def update_business(business_id: str, update: BusinessUpdate):
    try:
        update_dict = {k: v for k, v in update.model_dump().items()
                       if v is not None}

        if not update_dict:
            return JSONResponse(
                status_code=400,
                content={"message": "No valid fields to update", "error": True}
            )

        business_collection.find_one_and_update(
            {"business_id": business_id},
            {"$set": update_dict}
        )
        updated = business_collection.find_one({"business_id": business_id})

        if not updated:
            return JSONResponse(
                status_code=400,
                content={"message": "Business not found", "error": True}
            )

        # Trigger embedding update for the business
        embedding_result = process_and_embed_business(business_id)

        return JSONResponse(
            status_code=200,
            content={"message": "Business updated successfully",
                     "business": business_serial(updated),
                     "embedding_result": embedding_result}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )

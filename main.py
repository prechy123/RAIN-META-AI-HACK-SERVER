from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes.business_routes import router as BusinessRouter
from routes.whatsapp_routes import router as WhatsAppRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(BusinessRouter, prefix="/business", tags=["Business"])
app.include_router(WhatsAppRouter, prefix="/whatsapp", tags=["WhatsApp"])
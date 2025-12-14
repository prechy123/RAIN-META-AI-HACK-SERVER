from pydantic import BaseModel
from typing import Optional

class EmbedRequest(BaseModel):
    """Request model for embedding documents"""
    category: Optional[str] = None  # Filter by business category
    limit: Optional[int] = None  # Limit number of businesses to embed


class EmbedSingleBusinessRequest(BaseModel):
    """Request model for embedding a single business"""
    business_id: str  # Required: specific business to embed


class DeleteBusinessRequest(BaseModel):
    """Request model for deleting a business"""
    business_id: str


class EmbedResponse(BaseModel):
    """Response model for embedding operations"""
    status: str
    message: str
    total_businesses: int
    total_vectors: int
    changed_businesses: int
    skipped_businesses: int


class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    status: str
    message: str
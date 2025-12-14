from pydantic import BaseModel
from typing import Optional

class EmbedRequest(BaseModel):
    """Request model for embedding documents"""
    business_id: Optional[str] = None
    category: Optional[str] = None
    limit: Optional[int] = None


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
    deleted_count: int
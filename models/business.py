from pydantic import BaseModel, EmailStr
from typing import Optional, List

class BusinessItem(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class FAQ(BaseModel):
    question: str
    answer: str

class Business(BaseModel):
    email: EmailStr
    password: str
    business_id: str
    businessName: str
    businessDescription: str
    businessAddress: str
    businessPhone: str
    businessCategory: str
    businessOpenHours: Optional[str] = None
    businessOpenDays: Optional[str] = None
    businessWebsite: Optional[str] = None
    businessPicture: Optional[str] = None
    extra_information: Optional[str] = None
    faqs: Optional[List[FAQ]] = []
    items: Optional[List[BusinessItem]] = []

class BusinessUpdate(BaseModel):
    businessName: Optional[str] = None
    businessDescription: Optional[str] = None
    businessAddress: Optional[str] = None
    businessPhone: Optional[str] = None
    businessCategory: str
    businessOpenHours: Optional[str] = None
    businessOpenDays: Optional[str] = None
    businessWebsite: Optional[str] = None
    businessPicture: Optional[str] = None
    extra_information: Optional[str] = None
    faqs: Optional[List[FAQ]] = None
    items: Optional[List[BusinessItem]] = None
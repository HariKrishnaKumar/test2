# schemas/category.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Variation(BaseModel):
    id: str
    name: str
    price: float

    class Config:
        from_attributes = True

class Category(BaseModel):
    id: str
    name: str
    variations: List[Variation] = []

    class Config:
        from_attributes = True

# Pydantic models for parsing the response from the Clover API
class CloverVariation(BaseModel):
    id: str
    name: str
    price: int  # Clover returns price in cents

class CloverItem(BaseModel):
    id: str
    name: str
    price: int # Price in cents
    variants: Optional[List[CloverVariation]] = Field(default_factory=list)
    categories: Optional[dict]

class CloverCategory(BaseModel):
    id: str
    name: str
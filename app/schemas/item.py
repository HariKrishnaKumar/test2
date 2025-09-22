from pydantic import BaseModel
from typing import List

class ItemDetailRequest(BaseModel):
    """Schema for the item detail request body."""
    merchant_id: str
    item_id: str

class ItemDetailResponse(BaseModel):
    """Schema for the item detail response body."""
    merchant_id: str
    merchant_name: str
    item_id: str
    item_name: str
    types: List[str]
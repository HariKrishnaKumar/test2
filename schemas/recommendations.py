from pydantic import BaseModel
from typing import Optional

class RecommendationBase(BaseModel):
    user_id: int
    mobile_number: str
    item_id: str
    item_name: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationResponse(RecommendationBase):
    id: int

    class Config:
        from_attributes = True  # instead of orm_mode in Pydantic v2

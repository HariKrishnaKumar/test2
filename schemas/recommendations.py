from pydantic import BaseModel
from typing import Optional

class RecommendationBase(BaseModel):
    user_id: int
    item_id: str
    # item_name: Optional[str] = None
    # mobile_number: str
    
class RecommendationCreate(RecommendationBase):
    pass

class RecommendationResponse(RecommendationBase):
    id: int

    class Config:
        from_attributes = True  # instead of orm_mode in Pydantic v2

class RecommendationBase(BaseModel):
    user_id: int
    item_id: str

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    id: int

    class Config:
        from_attributes = True

class RecommendationUpdate(BaseModel):
    item_id: str
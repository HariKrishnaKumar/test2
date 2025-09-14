from pydantic import BaseModel
from typing import Optional

class UserUpdatePreferences(BaseModel):
    preferences: Optional[str] = None

class UserPreferencesResponse(BaseModel):
    id: int
    preferences: Optional[str] = None

    class Config:
        from_attributes = True
from fastapi import APIRouter, Depends, HTTPException
from schemas.preferences import UserUpdatePreferences, UserPreferencesResponse
from models.user import User
from sqlalchemy.orm import Session
from database.database import get_db

router = APIRouter()

@router.get("/users")
def get_users():
    return {"users": ["John", "Jane", "Bob"]}

@router.post("/users")
def create_user(name: str, email: str):
    return {"message": f"User {name} created with email {email}"}

# New endpoint to update user preferences
@router.put("/{user_id}/preferences", response_model=UserPreferencesResponse)
def update_user_preferences(user_id: int,
                            pref: UserUpdatePreferences,
                            db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.preferences = pref.preferences
    db.commit()
    db.refresh(user)
    return user
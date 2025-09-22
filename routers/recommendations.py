# # routers/recommendations.py

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# import requests
# from database.database import get_db
# from models.recommendation import Recommendation
# from models.user import User

# router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# CLOVER_API_BASE = "https://api.clover.com/v3/merchants"
# MERCHANT_ID = "<your_merchant_id>"
# ACCESS_TOKEN = "<your_api_key>"


# def fetch_item_name_from_clover(item_id: str) -> str:
#     url = f"{CLOVER_API_BASE}/{MERCHANT_ID}/items/{item_id}"
#     headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
#     resp = requests.get(url, headers=headers)
#     if resp.status_code == 200:
#         return resp.json().get("name", "Unknown Item")
#     return "Unknown Item"


# @router.post("/")
# def add_recommendation(user_id: int, item_id: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     recommendation = Recommendation(
#         user_id=user.id,
#         mobile_number=user.mobile_number,
#         item_id=item_id
#     )
#     db.add(recommendation)
#     db.commit()
#     db.refresh(recommendation)

#     return {
#         "id": recommendation.id,
#         "user_id": recommendation.user_id,
#         "mobile_number": recommendation.mobile_number,
#         "item_id": recommendation.item_id,
#         "item_name": fetch_item_name_from_clover(item_id)
#     }


# @router.get("/{rec_id}")
# def get_recommendation(rec_id: int, db: Session = Depends(get_db)):
#     rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
#     if not rec:
#         raise HTTPException(status_code=404, detail="Recommendation not found")

#     return {
#         "id": rec.id,
#         "user_id": rec.user_id,
#         "mobile_number": rec.mobile_number,
#         "item_id": rec.item_id,
#         "item_name": fetch_item_name_from_clover(rec.item_id)
#     }

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
import models.recommendations as models
import schemas.recommendations as schemas
from models import user as user_model
from models import recommendations as recommendation_model
from schemas import recommendations as recommendation_schema


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# Create recommendation
@router.post("/", response_model=schemas.RecommendationResponse)
def create_recommendation(rec: schemas.RecommendationCreate, db: Session = Depends(get_db)):
    new_rec = models.Recommendation(**rec.dict())
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec

# Get all recommendations
@router.get("/", response_model=list[schemas.RecommendationResponse])
def get_recommendations(db: Session = Depends(get_db)):
    return db.query(models.Recommendation).all()

@router.put("/{user_id}/recommendations/", response_model=recommendation_schema.Recommendation)
def update_user_recommendations(user_id: int, recommendation: recommendation_schema.RecommendationUpdate, db: Session = Depends(get_db)):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_recommendation = db.query(recommendation_model.Recommendation).filter(recommendation_model.Recommendation.user_id == user_id).first()

    if db_recommendation:
        db_recommendation.item_id = recommendation.item_id
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    else:
        # If no recommendation exists, create a new one
        new_recommendation = recommendation_model.Recommendation(user_id=user_id, item_id=recommendation.item_id)
        db.add(new_recommendation)
        db.commit()
        db.refresh(new_recommendation)
        return new_recommendation
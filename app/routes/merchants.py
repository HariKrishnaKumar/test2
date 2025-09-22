# app/routes/merchants.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from models.merchant import Merchant as MerchantModel
from services.clover_api import get_clover_categories, get_clover_items
from schemas.category import Category, Variation, CloverItem # Assuming schemas/category.py exists
from dependencies import get_clover_token

router = APIRouter()

# Schema for the /merchants endpoint
class MerchantInfo(BaseModel):
    id: int
    clover_merchant_id: str
    name: str

    class Config:
        from_attributes = True

# Endpoint to list all merchants
@router.get("/merchants", response_model=List[MerchantInfo])
def list_all_merchants(db: Session = Depends(get_db)):
    """
    Retrieves a list of all merchants from the database.
    """
    merchants = db.query(MerchantModel).all()
    return merchants

# Endpoint to get categories and variations from Clover
@router.get("/merchants/{merchant_id}/categories", response_model=List[Category])
async def get_merchant_categories_from_clover(
    merchant_id: int, # The ID from your local database
    db: Session = Depends(get_db),
    access_token: str = Depends(get_clover_token)
):
    """
    Retrieves all categories and their variations for a specific merchant
    by fetching data directly from the Clover API.
    """
    # --- START OF FIX ---
    # 1. Fetch the merchant from your database to get the real Clover ID.
    merchant = db.query(MerchantModel).filter(MerchantModel.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found in local database.")
    
    clover_merchant_id = merchant.clover_merchant_id
    # --- END OF FIX ---

    # 2. Call the Clover API with the correct Clover Merchant ID.
    clover_categories_data = await get_clover_categories(clover_merchant_id, access_token)
    clover_items_data = await get_clover_items(clover_merchant_id, access_token)

    # 3. Process the data (this part remains the same)
    categories_map = {
        cat['id']: Category(id=cat['id'], name=cat['name'], variations=[])
        for cat in clover_categories_data.get('elements', [])
    }

    for item_data in clover_items_data.get('elements', []):
        item = CloverItem(**item_data)
        if item.categories and item.categories.get('elements'):
            for category_ref in item.categories['elements']:
                category_id = category_ref['id']
                if category_id in categories_map:
                    if item.variants:
                        for variant_data in item.variants:
                            variation = Variation(
                                id=variant_data.id,
                                name=f"{item.name} ({variant_data.name})",
                                price=variant_data.price / 100.0
                            )
                            categories_map[category_id].variations.append(variation)
                    else:
                        variation = Variation(
                            id=item.id,
                            name=item.name,
                            price=item.price / 100.0
                        )
                        categories_map[category_id].variations.append(variation)

    return list(categories_map.values())
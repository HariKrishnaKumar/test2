from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from dependencies import get_clover_token
from services.clover_api import get_clover_merchant_details, get_clover_item_details
from app.schemas.item import ItemDetailRequest, ItemDetailResponse

from models.merchant import Merchant as MerchantModel # Add this import
from models.merchant_token import MerchantToken # Add this import
import asyncio

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.post("/details", response_model=ItemDetailResponse)
async def get_item_details_from_clover(
    request: ItemDetailRequest,
    db: Session = Depends(get_db)
):
    """
    Fetches the name of a merchant and the variations of a specific item
    directly from the Clover API.
    """
    # CORRECTED LOGIC TO FIND TOKEN
    # First, find the merchant in your DB using the Clover ID to get the internal ID
    merchant = db.query(MerchantModel).filter(MerchantModel.clover_merchant_id == request.merchant_id).first()
    
    # If the merchant doesn't exist in your database, you can't get a token
    if not merchant:
        raise HTTPException(
            status_code=404,
            detail=f"Merchant with Clover ID {request.merchant_id} not found in our system."
        )

    # Now, use the internal merchant.id to find the latest token
    token_record = db.query(MerchantToken)\
        .filter(MerchantToken.merchant_id == merchant.id)\
        .order_by(MerchantToken.created_at.desc())\
        .first()

    if not token_record or not token_record.token:
        raise HTTPException(
            status_code=404, # Changed to 404 to match the error you're seeing
            detail=f"No valid Clover API token found for merchant ID: {request.merchant_id}"
        )
    
    access_token = token_record.token

    # Fetch merchant and item details concurrently to save time
    try:
        merchant_details, item_details = await asyncio.gather(
            get_clover_merchant_details(request.merchant_id, access_token),
            get_clover_item_details(request.merchant_id, request.item_id, access_token)
        )
    except HTTPException as e:
        # Re-raise exceptions from the service layer to provide proper error feedback
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    # Extract variations/types from the item details
    variations = []
    if 'variants' in item_details and 'elements' in item_details['variants']:
        variations = [variant.get('name', 'Unnamed Variation') for variant in item_details['variants']['elements']]

    # If there are no variants, use a default value
    if not variations:
        variations.append("Standard")

    # Construct the final response
    response_data = ItemDetailResponse(
        merchant_id=request.merchant_id,
        merchant_name=merchant_details.get('name', 'Unknown Merchant'),
        item_id=request.item_id,
        item_name=item_details.get('name', 'Unknown Item'),
        types=variations
    )
    
    return response_data
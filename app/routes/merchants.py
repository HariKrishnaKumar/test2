# app/routes/merchants.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

from services.clover_api import get_clover_items, get_clover_categories
from schemas.category import Category, Variation as SchemaVariation, CloverItem # Assuming schemas/category.py exists

load_dotenv()

router = APIRouter()

CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL", "https://apisandbox.dev.clover.com")
CLOVER_ACCESS_TOKEN = os.getenv("CLOVER_ACCESS_TOKEN")
CLOVER_MERCHANT_ID = os.getenv("CLOVER_MERCHANT_ID")


# --- Schemas for Item Fetching ---
class Variation(BaseModel):
    id: str
    name: str
    price: int

class Item(BaseModel):
    id: str
    name: str
    price: int
    variations: List[Variation] = []

class MerchantItemsResponse(BaseModel):
    merchant_id: str
    items: List[Item]


# Schema for the /merchants endpoint
class MerchantInfo(BaseModel):
    clover_merchant_id: str
    name: str

    class Config:
        from_attributes = True

# --- NEW ENDPOINT TO FETCH ITEMS ---
@router.get("/merchants/{merchant_id}/items", response_model=MerchantItemsResponse)
async def get_merchant_items_from_clover(
    merchant_id: str  # The Clover Merchant ID from the URL
):
    """
    Retrieves all items and their variations for a specific merchant
    by fetching data directly from the Clover API.
    """
    if not CLOVER_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="Clover access token not configured.")

    try:
        # Call the Clover API to get items with variants expanded
        clover_items_data = await get_clover_items(merchant_id, CLOVER_ACCESS_TOKEN)

        formatted_items = []
        for item_data in clover_items_data.get("elements", []):
            variations = []
            if "variants" in item_data and "elements" in item_data["variants"]:
                for variant_data in item_data["variants"]["elements"]:
                    variations.append(
                        Variation(
                            id=variant_data.get("id"),
                            name=variant_data.get("name"),
                            price=variant_data.get("price", 0),
                        )
                    )

            formatted_items.append(
                Item(
                    id=item_data.get("id"),
                    name=item_data.get("name"),
                    price=item_data.get("price", 0),
                    variations=variations,
                )
            )

        return MerchantItemsResponse(merchant_id=merchant_id, items=formatted_items)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized: Please check your CLOVER_ACCESS_TOKEN.")
        raise HTTPException(status_code=e.response.status_code, detail=f"Clover API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# Endpoint to list all merchants
@router.get("/merchants", response_model=List[MerchantInfo])
async def list_all_merchants():
    """
    Retrieves merchant details directly from the Clover API using credentials from the .env file.
    """
    if not CLOVER_ACCESS_TOKEN or not CLOVER_MERCHANT_ID:
        raise HTTPException(
            status_code=500,
            detail="Clover credentials not configured in .env file."
        )

    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}"
    headers = {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            merchant_data = response.json()

            merchant_info = MerchantInfo(
                clover_merchant_id=merchant_data.get("id"),
                name=merchant_data.get("name")
            )

            return [merchant_info]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise HTTPException(status_code=401, detail="Unauthorized: Please check your CLOVER_ACCESS_TOKEN.")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Clover API error: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}"
            )

# Endpoint to get categories and variations from Clover
@router.get("/merchants/{merchant_id}/categories", response_model=List[Category])
async def get_merchant_categories_from_clover(
    merchant_id: str # The Clover Merchant ID from the URL
):
    """
    Retrieves all categories and their variations for a specific merchant
    by fetching data directly from the Clover API.
    """
    if not CLOVER_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="Clover access token not configured.")

    try:
        # Call the Clover API with the correct Clover Merchant ID.
        clover_categories_data = await get_clover_categories(merchant_id, CLOVER_ACCESS_TOKEN)
        clover_items_data = await get_clover_items(merchant_id, CLOVER_ACCESS_TOKEN)

        # Process the data
        categories_map = {
            cat['id']: Category(id=cat['id'], name=cat['name'], variations=[])
            for cat in clover_categories_data.get('elements', [])
        }
        
        # Create a default category for uncategorized items
        uncategorized = Category(id="uncategorized", name="Uncategorized", variations=[])
        
        for item_data in clover_items_data.get('elements', []):
            item = CloverItem(**item_data)
            
            # Check if the item has categories
            if item.categories and item.categories.get('elements'):
                for category_ref in item.categories['elements']:
                    category_id = category_ref['id']
                    if category_id in categories_map:
                        if item.variants:
                            for variant_data in item.variants:
                                variation = SchemaVariation(
                                    id=variant_data.id,
                                    name=f"{item.name} ({variant_data.name})",
                                    price=variant_data.price / 100.0
                                )
                                categories_map[category_id].variations.append(variation)
                        else:
                            variation = SchemaVariation(
                                id=item.id,
                                name=item.name,
                                price=item.price / 100.0
                            )
                            categories_map[category_id].variations.append(variation)
            else:
                # If the item has no categories, add it to the "Uncategorized" list
                if item.variants:
                    for variant_data in item.variants:
                        variation = SchemaVariation(
                            id=variant_data.id,
                            name=f"{item.name} ({variant_data.name})",
                            price=variant_data.price / 100.0
                        )
                        uncategorized.variations.append(variation)
                else:
                    variation = SchemaVariation(
                        id=item.id,
                        name=item.name,
                        price=item.price / 100.0
                    )
                    uncategorized.variations.append(variation)

        # Combine the categorized and uncategorized items
        final_categories = list(categories_map.values())
        if uncategorized.variations:
            final_categories.append(uncategorized)
            
        return final_categories
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized: Please check your CLOVER_ACCESS_TOKEN.")
        raise HTTPException(status_code=e.response.status_code, detail=f"Clover API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
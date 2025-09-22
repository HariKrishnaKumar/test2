import httpx
import os
from fastapi import HTTPException

BASE_URL = os.getenv("CLOVER_BASE_URL", "https://apisandbox.dev.clover.com/v3/merchants")


class CloverAPI:
    def __init__(self, merchant_id: str, access_token: str):
        self.merchant_id = merchant_id
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def get_items(self, limit: int = 100, offset: int = 0, expand: str | None = None):
        url = f"{BASE_URL}/{self.merchant_id}/items"
        params = {"limit": limit, "offset": offset}
        if expand:
            params["expand"] = expand
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers, params=params)
            return r.json()

    async def get_categories(self, limit: int = 100, offset: int = 0):
        url = f"{BASE_URL}/{self.merchant_id}/categories"
        params = {"limit": limit, "offset": offset}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers, params=params)
            return r.json()

    async def get_modifier_groups(self, limit: int = 100, offset: int = 0):
        url = f"{BASE_URL}/{self.merchant_id}/modifier_groups"
        params = {"limit": limit, "offset": offset}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers, params=params)
            return r.json()

    # DEFINE THE HELPER FUNCTION FIRST
async def make_clover_api_request(merchant_id: str, access_token: str, endpoint: str):
    """
    A reusable function for making authenticated GET requests to the Clover API.
    """
    base_url = f"https://api.clover.com/v3/merchants/{merchant_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/{endpoint}", headers=headers)
            response.raise_for_status()  # This will raise an exception for 4XX or 5XX status codes
            return response.json()
        except httpx.HTTPStatusError as e:
            # Provide more specific error details from Clover if available
            detail = e.response.json().get("message", "Error fetching data from Clover API")
            raise HTTPException(status_code=e.response.status_code, detail=detail)
        except httpx.RequestError as e:
            # Handle network-related errors
            raise HTTPException(status_code=500, detail=f"A network error occurred: {e}")

# NOW DEFINE THE FUNCTIONS THAT USE THE HELPER
async def get_clover_categories(merchant_id: str, access_token: str):
    """Fetches all categories for a given merchant from the Clover API."""
    return await make_clover_api_request(merchant_id, access_token, "categories")

async def get_clover_items(merchant_id: str, access_token: str):
    """
    Fetches all items for a merchant, expanding to include variants and categories.
    """
    return await make_clover_api_request(merchant_id, access_token, "items?expand=variants,categories")


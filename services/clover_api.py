import httpx
import os
from fastapi import HTTPException

# Use the environment variable for the base URL, with a fallback
BASE_URL = os.getenv("CLOVER_BASE_URL", "https://apisandbox.dev.clover.com")


class CloverAPI:
    def __init__(self, merchant_id: str, access_token: str):
        self.merchant_id = merchant_id
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def get_items(self, limit: int = 100, offset: int = 0, expand: str | None = None):
        url = f"{BASE_URL}/v3/merchants/{self.merchant_id}/items"
        params = {"limit": limit, "offset": offset}
        if expand:
            params["expand"] = expand
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    async def get_categories(self, limit: int = 100, offset: int = 0):
        url = f"{BASE_URL}/v3/merchants/{self.merchant_id}/categories"
        params = {"limit": limit, "offset": offset}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    async def get_modifier_groups(self, limit: int = 100, offset: int = 0):
        url = f"{BASE_URL}/v3/merchants/{self.merchant_id}/modifier_groups"
        params = {"limit": limit, "offset": offset}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

async def make_clover_api_request(merchant_id: str, access_token: str, endpoint: str):
    """
    A reusable function for making authenticated GET requests to the Clover API.
    This function now allows HTTPStatusError to be handled by the calling route.
    """
    url = f"{BASE_URL}/v3/merchants/{merchant_id}/{endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raises HTTPStatusError for 4XX/5XX responses
            return response.json()
        except httpx.RequestError as e:
            # Handle network-related errors
            raise HTTPException(status_code=500, detail=f"A network error occurred: {e}")

async def get_clover_categories(merchant_id: str, access_token: str):
    """Fetches all categories for a given merchant from the Clover API."""
    return await make_clover_api_request(merchant_id, access_token, "categories")

async def get_clover_items(merchant_id: str, access_token: str):
    """
    Fetches all items for a merchant, expanding to include variants and categories.
    """
    return await make_clover_api_request(merchant_id, access_token, "items?expand=variants,categories")
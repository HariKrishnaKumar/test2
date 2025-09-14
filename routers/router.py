from fastapi import APIRouter
from app.routes import select_routes, voice_routes

api_router = APIRouter()

# Include route modules
api_router.include_router(
    select_routes.router,
    prefix="/select",
    tags=["Select Mode"]
)

api_router.include_router(
    voice_routes.router,
    prefix="/voice",
    tags=["Voice Mode"]
)

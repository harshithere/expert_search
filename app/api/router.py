from fastapi import APIRouter
from app.api.endpoints import ingest, search

api_router = APIRouter()

api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(search.router, prefix="/search", tags=["search"])

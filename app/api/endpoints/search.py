from fastapi import APIRouter
from app.services.search import SearchVectorDb
from typing import Optional

router = APIRouter()
search_vector_db = SearchVectorDb()


@router.post("/search")
def search_vector_db(query: str, conversation_id: Optional[str] = None):
    """
    Endpoint for querying the Vector DB.
    """
    results = search_vector_db.search(query, conversation_id)
    return {"query": query, "results": results}
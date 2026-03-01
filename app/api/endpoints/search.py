from fastapi import APIRouter
from app.services.search import SearchVectorDb
from app.models.search import SearchRequest
from typing import Optional

router = APIRouter()
search_vector_db = SearchVectorDb()


@router.post("/search")
def search_VB(query: str, conversation_id: Optional[str] = None):
    """
    Endpoint for querying the Vector DB.
    """
    results = search_vector_db.search(query, conversation_id)
    return {"query": query, "results": results}

if __name__ == "__main__":
    print(search_VB("Specialist specializing in linear algebra"))

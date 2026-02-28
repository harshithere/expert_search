from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def search_vector_db(query: str):
    """
    Endpoint for querying the Vector DB.
    """
    return {"query": query, "results": []}

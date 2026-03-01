from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.ingest import Candidate


class SearchRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None


class SearchResponse(BaseModel):
    status: str
    query: str
    candidates: List[Candidate]
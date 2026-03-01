from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
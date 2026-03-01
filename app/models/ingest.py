from pydantic import BaseModel, Field
from typing import List, Optional

class Candidate(BaseModel):
    candidate_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    dob: str
    gender: str
    job_id: str
    title: str
    bio: str
    experience: int
    created_at: str

    
from pydantic import BaseModel, Field
from typing import List, Optional


class WorkExperience(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class Candidate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    experience: Optional[int] = None
    work_experience: Optional[List[WorkExperience]] = None

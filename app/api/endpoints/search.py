from fastapi import APIRouter
from app.services.search import SearchVectorDb
from app.models.search import SearchRequest, SearchResponse
from app.models.ingest import Candidate, WorkExperience

router = APIRouter()
search_vector_db = SearchVectorDb()


def _parse_candidate(node_with_score) -> Candidate:
    node = node_with_score.node
    metadata = node.metadata

    name_parts = metadata.get("candidate_name", "").split(" ", 1)
    first_name = name_parts[0] or None
    last_name = name_parts[1] if len(name_parts) > 1 else None

    bio = None
    work_experiences = []
    for line in node.text.split("\n"):
        if line.startswith("Headline: "):
            bio = line.removeprefix("Headline: ")
        elif line.startswith("Work Experience: "):
            work_experiences.append(
                WorkExperience(description=line.removeprefix("Work Experience: "))
            )

    return Candidate(
        first_name=first_name,
        last_name=last_name,
        bio=bio,
        experience=metadata.get("experience"),
        work_experience=work_experiences or None,
    )


@router.post("/search", response_model=SearchResponse)
def search_VB(request: SearchRequest):
    """
    Endpoint for querying the Vector DB.
    """
    response = search_vector_db.search(request.query, request.conversation_id)
    candidates = [_parse_candidate(node) for node in response.source_nodes]
    return SearchResponse(status="success", query=request.query, candidates=candidates)

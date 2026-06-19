from fastapi import APIRouter, HTTPException

from app.schemas import AiExplainRequest, AiExplainResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/explain", response_model=AiExplainResponse)
def explain_error(_payload: AiExplainRequest) -> AiExplainResponse:
    raise HTTPException(
        status_code=501,
        detail="AI-подсказки будут добавлены позже. Endpoint зарезервирован.",
    )

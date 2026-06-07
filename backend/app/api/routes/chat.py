from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agents.graph import run_agent_workflow
from app.services.evaluation.query_logger import log_query

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    response = await run_agent_workflow(request)
    log_query(request, response)
    return response

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.base_agent import run_agent

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    response = run_agent(request.message)
    return response

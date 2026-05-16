from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    assistant_answer: str
    query: str
    count: int
    files: list
    error: str | None = None

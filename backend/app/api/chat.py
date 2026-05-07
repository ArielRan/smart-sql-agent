from fastapi import APIRouter
from pydantic import BaseModel
from app.services.agent_service import chat

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def do_chat(req: ChatRequest):
    return chat(req.question)
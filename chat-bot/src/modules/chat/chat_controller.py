from dataclasses import dataclass
from fastapi import APIRouter
from agents.base_agent.claude_agent import ClaudeAgent

router = APIRouter(prefix="/chat")


@dataclass
class ChatRequest:
    message: str


@router.post("/")
def chat(body: ChatRequest):
    model = ClaudeAgent()
    # result = model.chat(body.message)
    result = model.chat_with_mcp(body.message)

    return {
        "response": result
    }
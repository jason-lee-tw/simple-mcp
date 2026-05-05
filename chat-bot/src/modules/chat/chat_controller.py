from dataclasses import dataclass
from fastapi import APIRouter
from agents.base_agent.claude_agent import ClaudeAgent

router = APIRouter(prefix="/chat")


@dataclass
class ChatRequest:
    message: str


@router.post("/")
def chat(body: ChatRequest):
    system_prompt="""You are a assistant that having access to memory tools.
## Get memory

- When calling tools to get memory, ALWAYS use as much as relevant keywords. As the tool is using keyword based searching.

## Store memory

- MUST memorise user's preference, so you can answer better according to the user's preference.
- Memories must be stored as detailed as possible, so it can be higher chance to be queried.
"""
    model = ClaudeAgent(system_prompt)
    # result = model.chat(body.message)
    result = model.chat_with_mcp(body.message)

    return {
        "response": result
    }
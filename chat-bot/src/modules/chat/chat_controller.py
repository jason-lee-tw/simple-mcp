from fastapi import APIRouter

router = APIRouter(prefix="/chat")


@router.post("/")
def chat():
    return {}
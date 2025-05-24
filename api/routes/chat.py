# api/routes/chat.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def chat_root():
    return {"message": "Chat endpoint is live"}

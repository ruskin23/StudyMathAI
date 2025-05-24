# api/routes/search.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def chat_root():
    return {"message": "Search endpoint is live"}

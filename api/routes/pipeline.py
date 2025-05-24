# api/routes/pipeline.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def chat_root():
    return {"message": "Pipeline endpoint is live"}

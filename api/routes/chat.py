# api/routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
from studymathai.chatbot import ContextAwareChatBot, ChatContextManager
from studymathai.retriever import SlideRetriever
from studymathai.db import DatabaseConnection

router = APIRouter()
db = DatabaseConnection()

# ──────────────── Request & Response Models ────────────────

class ChatQuery(BaseModel):
    session_id: str
    query: str

class SlideDeck(BaseModel):
    segment_id: int
    heading: str
    slides: List[Dict[str, Any]]

class ChatResponse(BaseModel):
    response: str
    retrieved_slides: Optional[List[SlideDeck]] = None

class ChatHistory(BaseModel):
    session_id: str
    history: list


# ──────────────── Chat Endpoints ────────────────

@router.post("/query", response_model=ChatResponse)
def chat_query(data: ChatQuery):
    try:
        history_file = f"chat_history_{data.session_id}.json"
        context_manager = ChatContextManager(history_file=history_file)
        retriever = SlideRetriever(db=db)
        
        chatbot = ContextAwareChatBot(retriever=retriever, context_manager=context_manager)
        reply, retrieved_slides = chatbot.get_response(data.query, return_context=True)
        return ChatResponse(response=reply, retrieved_slides=retrieved_slides)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=ChatHistory)
def get_chat_history(session_id: str):
    history_file = f"chat_history_{session_id}.json"
    if not os.path.exists(history_file):
        raise HTTPException(status_code=404, detail="Session history not found")
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
        return ChatHistory(session_id=session_id, history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

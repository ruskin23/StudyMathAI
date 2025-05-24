# api/main.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, search, books, pipeline


app = FastAPI(title="StudyMathAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 

# Register routes
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

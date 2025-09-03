# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import books, content, extract
from studymathai.database import DatabaseConnection

app = FastAPI(title="StudyMathAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add DB connection
app.state.db_connection = DatabaseConnection()

# Register routes
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(extract.router, prefix="/extract", tags=["Extract"])
app.include_router(content.router, prefix="/content", tags=["Content"])


@app.get("/health")
def health_check():
    return {"status": "ok"}

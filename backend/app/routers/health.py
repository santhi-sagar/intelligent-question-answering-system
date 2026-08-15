from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import get_db
from ..config import settings


router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    # Check DB
    db.execute(text("SELECT 1"))
    # Check OpenAI key presence only (no network call)
    embeddings_ready = settings.openai_api_key is not None and len(settings.openai_api_key) > 0
    return {"status": "ok", "db": True, "embeddings_ready": embeddings_ready}



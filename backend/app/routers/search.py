from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db


router = APIRouter()


@router.get("/search")
def search(query: str = Query(...), k: int = Query(5), db: Session = Depends(get_db)):
    # Placeholder search response; full pgvector search implemented in retriever.
    return {"query": query, "results": [], "k": k}



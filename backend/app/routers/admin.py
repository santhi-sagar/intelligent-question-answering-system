from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..db import get_db
from ..models import Document, Chunk


router = APIRouter()


@router.get("/admin/docs")
def list_docs(db: Session = Depends(get_db)):
    q = (
        db.execute(
            select(Document.id, Document.title, func.count(Chunk.id))
            .select_from(Document)
            .join(Chunk, Chunk.doc_id == Document.id, isouter=True)
            .group_by(Document.id, Document.title)
        )
        .tuples()
        .all()
    )
    return [{"id": str(i), "title": t, "chunk_count": c} for (i, t, c) in q]


@router.delete("/admin/doc/{doc_id}")
def delete_doc(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}


@router.post("/admin/reindex")
def reindex_placeholder():
    return {"status": "ok"}



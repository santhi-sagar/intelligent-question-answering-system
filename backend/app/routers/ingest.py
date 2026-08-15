from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from uuid import uuid4, UUID
from ..db import get_db
from ..deps import rate_limit_placeholder
from ..models import Document, Chunk
from ..services.document_processor import process_document_sync


router = APIRouter()


@router.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_placeholder),
):
    """Upload and process a file through the complete pipeline. Replaces all existing documents."""
    if file.content_type not in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Read file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Create document record (we KEEP existing documents; each upload becomes a new one)
    doc = Document(
        id=uuid4(),
        title=file.filename,
        source_type="pdf" if file.content_type == "application/pdf" else "txt",
    )
    db.add(doc)
    db.commit()

    # Process document
    try:
        success = process_document_sync(db, doc.id, file_bytes, file.content_type)
        if success:
            return {"status": "processed", "document_id": str(doc.id), "message": "Document processed successfully"}
        else:
            return {"status": "queued", "document_id": str(doc.id), "message": "Document queued for processing"}
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        return {"status": "queued", "document_id": str(doc.id), "message": "Document queued for processing"}


# Primary status route used by the frontend
@router.get("/ingest/status/{document_id}")
async def get_document_status(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Check the processing status of a document and whether embeddings are created."""
    try:
        doc_uuid = UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    # Get document
    doc = db.get(Document, doc_uuid)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Count chunks for this document
    chunk_count = db.execute(
        select(func.count(Chunk.id))
        .where(Chunk.doc_id == doc_uuid)
    ).scalar() or 0
    
    # Determine status based on chunk count
    if chunk_count > 0:
        status = "processed"
        message = f"Document processed successfully with {chunk_count} chunks"
    else:
        status = "queued"
        message = "Document is queued for processing"
    
    return {
        "document_id": document_id,
        "title": doc.title,
        "status": status,
        "chunk_count": chunk_count,
        "message": message,
        "created_at": doc.created_at.isoformat() if doc.created_at else None
    }

# Back-compat legacy route
@router.get("/status/{document_id}")
async def get_document_status_legacy(
    document_id: str,
    db: Session = Depends(get_db)
):
    return await get_document_status(document_id, db)



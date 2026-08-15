"""
Document Processing Service
Handles the complete pipeline from file upload to vector storage
"""

import asyncio
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID

from ..models import Document, Chunk
from ..rag.embed import embed_texts
from .file_loaders import load_pdf, load_docx, load_text, load_csv_xlsx
from .chunking import chunk_text

PLACEHOLDER_SNIPPETS = [
    "no text content found",
    "empty text file",
    "no data found in spreadsheet",
    "error loading pdf",
    "error loading docx",
    "error loading text file",
    "error loading spreadsheet",
]


def process_document(db: Session, document_id: UUID, file_bytes: bytes, content_type: str) -> bool:
    """
    Process a document through the complete pipeline:
    1. Extract text content
    2. Create chunks
    3. Generate embeddings
    4. Store in database
    """
    try:
        print(f"Processing document {document_id} with content type {content_type}")
        
        # Step 1: Extract text content based on file type
        pages = extract_text_content(file_bytes, content_type)
        pages = _remove_placeholder_pages(pages)
        if not pages:
            print(f"No text content extracted from document {document_id}")
            return False
        
        print(f"Extracted {len(pages)} pages from document {document_id}")
        
        # Step 2: Create chunks
        chunks = chunk_text(pages, max_tokens=1000, overlap=150)
        if not chunks:
            print(f"No chunks created from document {document_id}")
            return False
        
        print(f"Created {len(chunks)} chunks from document {document_id}")
        
        # Step 3: Generate embeddings for all chunks
        chunk_texts = [chunk[1] for chunk in chunks]  # Extract text from (page_no, text) tuples
        embeddings = generate_embeddings(chunk_texts)
        
        if not embeddings or len(embeddings) != len(chunks):
            print(f"Failed to generate embeddings for document {document_id}")
            return False
        
        print(f"Generated {len(embeddings)} embeddings for document {document_id}")
        
        # Step 4: Store chunks with embeddings in database
        success = store_chunks_with_embeddings(db, document_id, chunks, embeddings)
        
        if success:
            print(f"Successfully processed document {document_id}")
        else:
            print(f"Failed to store chunks for document {document_id}")
        
        return success
        
    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")
        return False


def extract_text_content(file_bytes: bytes, content_type: str) -> List[Tuple[int, str]]:
    """Extract text content from file based on content type."""
    try:
        if content_type == "application/pdf":
            return load_pdf(file_bytes)
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return load_docx(file_bytes)
        elif content_type == "text/plain":
            return load_text(file_bytes)
        elif content_type == "text/csv":
            return load_csv_xlsx(file_bytes, is_xlsx=False)
        elif content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return load_csv_xlsx(file_bytes, is_xlsx=True)
        else:
            print(f"Unsupported content type: {content_type}")
            return []
    except Exception as e:
        print(f"Error extracting text content: {str(e)}")
        return []


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts."""
    try:
        if not texts:
            return []
        
        # Use the existing embed_texts function
        embeddings = embed_texts(texts)
        return embeddings
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return []


def store_chunks_with_embeddings(
    db: Session, 
    document_id: UUID, 
    chunks: List[Tuple[int, str]], 
    embeddings: List[List[float]]
) -> bool:
    """Store chunks with their embeddings in the database."""
    try:
        # Delete existing chunks for this document
        db.execute(text("DELETE FROM chunks WHERE doc_id = :doc_id"), {"doc_id": str(document_id)})
        
        # Insert new chunks with embeddings
        for i, ((page_no, content), embedding) in enumerate(zip(chunks, embeddings)):
            # Calculate token count (approximate)
            token_count = len(content.split()) * 1.3  # Rough approximation
            
            # Convert embedding list to string format for pgvector: '[0.1,0.2,0.3]'
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            # Insert chunk with embedding using raw SQL for pgvector
            db.execute(text("""
                INSERT INTO chunks (id, doc_id, content, page_no, token_count, embedding, created_at)
                VALUES (
                    gen_random_uuid(),
                    :doc_id,
                    :content,
                    :page_no,
                    :token_count,
                    CAST(:embedding AS vector),
                    NOW()
                )
            """), {
                "doc_id": str(document_id),
                "content": content,
                "page_no": page_no,
                "token_count": int(token_count),
                "embedding": embedding_str
            })
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"Error storing chunks with embeddings: {str(e)}")
        db.rollback()
        return False


def process_document_sync(db: Session, document_id: UUID, file_bytes: bytes, content_type: str) -> bool:
    """Synchronous wrapper for document processing."""
    return process_document(db, document_id, file_bytes, content_type)


def _remove_placeholder_pages(pages: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    """Remove placeholder strings that indicate missing or unreadable content."""
    cleaned = []
    for page_no, text in pages:
        if not text:
            continue
        lowered = text.strip().lower()
        if any(snippet in lowered for snippet in PLACEHOLDER_SNIPPETS):
            continue
        cleaned.append((page_no, text))
    return cleaned

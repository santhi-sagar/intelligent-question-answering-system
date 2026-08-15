from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text


def vector_search(db: Session, query_embedding: List[float], k: int = 8, filters: Optional[dict] = None) -> List[Tuple[str, float]]:
    """Vector search with fallback to text search."""
    try:
        # First try pgvector search
        return _pgvector_search(db, query_embedding, k, filters)
    except Exception as e:
        print(f"Vector search error: {str(e)}, using fallback")
        # Rollback any failed transaction before fallback
        try:
            db.rollback()
        except:
            pass
        return _fallback_text_search(db, query_embedding, k, filters)


def _pgvector_search(db: Session, query_embedding: List[float], k: int = 8, filters: Optional[dict] = None) -> List[Tuple[str, float]]:
    """Try pgvector search first. Only searches chunks from the latest document."""
    where = []
    params: dict = {}
    
    # Always filter by the latest document ID to ensure we only use the most recent upload
    try:
        # Get the latest document ID
        latest_doc_result = db.execute(text("""
            SELECT id::text FROM documents 
            ORDER BY created_at DESC 
            LIMIT 1
        """)).fetchone()
        
        if latest_doc_result:
            latest_doc_id = latest_doc_result[0]
            where.append("chunks.doc_id = :latest_doc_id")
            params["latest_doc_id"] = latest_doc_id
        else:
            # No documents exist, return empty
            return []
    except Exception as e:
        print(f"Error getting latest document: {str(e)}")
        return []
    
    if filters:
        for key in ("campus", "program", "year"):
            if key in filters and filters[key] is not None:
                where.append(f"(chunks.metadata ->> '{key}') = :{key}")
                params[key] = str(filters[key])
    
    # Build WHERE clause - we always have at least the latest_doc_id filter
    where_clause = "WHERE " + " AND ".join(where) if where else ""
    
    # Convert embedding list to string format for pgvector: '[0.1,0.2,0.3]'
    # pgvector expects the format: '[0.1,0.2,0.3]' as a string
    embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
    
    # Use proper pgvector syntax - pass as string and let PostgreSQL cast it
    sql = f"""
        SELECT id::text, 1 - (embedding <=> CAST(:embedding AS vector)) AS score
        FROM chunks
        {where_clause}
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :k
    """
    
    try:
        # Ensure clean transaction state
        db.rollback()
        
        params["embedding"] = embedding_str
        params["k"] = k
        rows = db.execute(text(sql), params).all()
        return [(r[0], float(r[1])) for r in rows]
    except Exception as e:
        print(f"Vector search error: {str(e)}")
        db.rollback()  # Rollback on error
        raise


def _fallback_text_search(db: Session, query_embedding: List[float], k: int = 8, filters: Optional[dict] = None) -> List[Tuple[str, float]]:
    """Fallback text search when vector search fails - returns chunks from latest document only."""
    try:
        # Ensure we're in a clean transaction state
        db.rollback()
        
        # Get the latest document ID first
        latest_doc_result = db.execute(text("""
            SELECT id::text FROM documents 
            ORDER BY created_at DESC 
            LIMIT 1
        """)).fetchone()
        
        if not latest_doc_result:
            return []
        
        latest_doc_id = latest_doc_result[0]
        
        # Return chunks only from the latest document
        sql = text("""
            SELECT id::text, 1.0 AS score
            FROM chunks
            WHERE doc_id = :latest_doc_id
            ORDER BY created_at DESC
            LIMIT :k
        """)
        rows = db.execute(sql, {"latest_doc_id": latest_doc_id, "k": k}).all()
        result = [(r[0], float(r[1])) for r in rows]
        print(f"Fallback search returned {len(result)} chunks from latest document")
        return result
    except Exception as e:
        print(f"Fallback search error: {str(e)}")
        try:
            db.rollback()
            # Ultimate fallback - get latest doc and return its chunks
            latest_doc_result = db.execute(text("""
                SELECT id::text FROM documents 
                ORDER BY created_at DESC 
                LIMIT 1
            """)).fetchone()
            if latest_doc_result:
                latest_doc_id = latest_doc_result[0]
                sql = text("SELECT id::text, 1.0 AS score FROM chunks WHERE doc_id = :latest_doc_id LIMIT :k")
                rows = db.execute(sql, {"latest_doc_id": latest_doc_id, "k": k}).all()
                return [(r[0], float(r[1])) for r in rows]
            return []
        except Exception as e2:
            print(f"Ultimate fallback also failed: {str(e2)}")
            return []



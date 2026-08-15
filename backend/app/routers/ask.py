from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import AskRequest, AskResponse
from ..rag.pipeline import run_pipeline


router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    """Process a question through the RAG pipeline."""
    try:
        # Use the RAG pipeline to generate response
        response = run_pipeline(db, req.question, filters=None)
        return response
    except Exception as e:
        print(f"Error in ask endpoint: {str(e)}")
        # Return a fallback response if RAG pipeline fails
        return AskResponse(
            answer_html="<p>I'm sorry, I encountered an error processing your question. Please try again.</p>",
            citations=[],
            followups=["Try rephrasing your question", "Upload more documents"],
            query_rewrite=req.question,
            safety_notes="",
        )



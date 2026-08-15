import json
import re
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from .embed import embed_texts
from .retriever import vector_search
from .rerank import mmr_rerank
from .llm_client import get_llm_response, is_llm_available
from ..schemas import AskResponse, Citation
from ..config import settings
from ..rag.system_prompt import SYSTEM_PROMPT

QUESTION_STOPWORDS = {
    "what",
    "where",
    "when",
    "which",
    "who",
    "whom",
    "whose",
    "how",
    "explain",
    "tell",
    "about",
    "more",
    "give",
    "show",
    "list",
    "describe",
    "detail",
    "details",
    "information",
    "info",
    "please",
    "kindly",
    "help",
    "need",
    "share",
    "guide",
    "find",
    "location",
    "located",
    "address",
    "regarding",
    "regards",
    "know",
    "want",
    "explanation",
    "provide",
    "about",
}


def _is_general_question(question: str) -> bool:
    """Check if the question is a general greeting or conversational question."""
    if not question or not question.strip():
        return False
        
    question_lower = question.lower().strip()
    
    # Remove punctuation for better matching
    question_clean = question_lower.replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip()
    
    # Common greetings - exact matches (check both original and cleaned)
    greetings_exact = ["hi", "hello", "hey", "howdy", "greetings", "hi there", "hello there", 
                       "hey there", "good morning", "good afternoon", "good evening", "good night"]
    
    # Check exact match first (both with and without punctuation)
    if question_lower in greetings_exact or question_clean in greetings_exact:
        return True
    
    # Check if it starts with a greeting
    greeting_starts = ["hi ", "hello ", "hey ", "good morning", "good afternoon", "good evening", "good night"]
    if any(question_lower.startswith(g) for g in greeting_starts):
        return True
    
    # General conversational questions (including variations and typos)
    general_patterns = [
        "how are you", "how r you", "how are u", "how r u", "how do you do",
        "what can you do", "what do you do", "who are you",
        "tell me about yourself", "what is this", "what is srm unichat",
        "help me", "can you help", "what help", "assist me", "what's up",
        "whats up", "what are you", "what can you", "introduce yourself"
    ]
    
    # Check if it matches general patterns
    if any(pattern in question_lower for pattern in general_patterns):
        return True
    
    # Very short questions (1-2 words) that are likely greetings
    words = question_clean.split()
    if len(words) <= 2:
        # Check if any word is a greeting
        greeting_words = ["hi", "hello", "hey", "howdy", "greetings"]
        if any(word in greeting_words for word in words):
            return True
    
    return False


def _generate_general_response(question: str) -> AskResponse:
    """Generate a response for general questions without requiring documents using LLM (Gemini or OpenAI)."""
    # Check if any LLM is available
    if not is_llm_available():
        return AskResponse(
            answer_html="No AI API key is configured. Please add your GEMINI_API_KEY (free) or OPENAI_API_KEY to the .env file and restart the backend.",
            citations=[],
            followups=["Configure API key", "Get Gemini API key (free)"],
            query_rewrite=question,
            safety_notes="",
        )
    
    system_prompt = "You are SRM UniChat, a friendly and helpful AI assistant. You can answer ANY general question conversationally, just like ChatGPT. You're specialized in helping with SRM University questions, but you can also answer general knowledge questions, have conversations, help with explanations, and more. Be natural, conversational, and helpful. Don't mention document uploads unless the user specifically asks about document content or needs very specific data that would require uploaded documents. Keep responses concise but complete. IMPORTANT: Do NOT use HTML tags like <p>, <strong>, etc. in your responses. Use plain text only."
    
    try:
        answer_text = get_llm_response(question, system_prompt)
        
        if answer_text:
            answer = answer_text
            followups = [
                "Tell me about SRM University",
                "What can you help me with?",
                "How do I upload documents?"
            ]
        else:
            # If we get None, it means both APIs failed but not with API key errors
            # This could be network issues, rate limits, or other temporary problems
            answer = "I'm having trouble connecting to the AI service right now. This might be a temporary issue. Please try again in a moment."
            followups = [
                "Try again",
                "Check API configuration",
                "Get Gemini API key (free)"
            ]
    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()
        # Check if it's specifically an API key error
        if "api key" in error_lower or "api_key" in error_lower:
            answer = error_msg
        else:
            # Other errors (network, rate limits, etc.)
            answer = f"I encountered an error: {error_msg}. Please try again."
        followups = [
            "Check API configuration",
            "Get Gemini API key (free)",
            "Try again"
        ]
    
    return AskResponse(
        answer_html=answer,
        citations=[],
        followups=followups,
        query_rewrite=question,
        safety_notes="",
    )


def run_pipeline(db: Session, question: str, filters: Dict[str, Any] | None = None) -> AskResponse:
    """Run the complete RAG pipeline - uses documents when available, combines with general knowledge."""
    try:
        # Check if this is a simple greeting first
        is_general = _is_general_question(question)
        if is_general:
            return _generate_general_response(question)
        
        # For every non-greeting, first search uploaded documents. The relevance
        # check below decides whether to answer from retrieved chunks or general knowledge.
        # This allows natural questions such as "What are the library hours?" to use
        # uploaded content without requiring the user to say "from the document".
        needs_doc_context = True

        # Query rewrite placeholder: identity
        query_rewrite = question

        # Embed query
        query_vec = embed_texts([query_rewrite])[0]

        # First, check if any documents exist in the database
        try:
            doc_count = db.execute(text("SELECT COUNT(*) FROM documents")).scalar()
            chunk_count = db.execute(text("SELECT COUNT(*) FROM chunks")).scalar()
            print(f"Documents in DB: {doc_count}, Chunks in DB: {chunk_count}")
        except Exception as e:
            print(f"Error checking document count: {str(e)}")
            doc_count = 0
            chunk_count = 0

        # Retrieve relevant chunks from uploaded documents
        retrieved = []
        try:
            retrieved = vector_search(db, query_vec, k=8, filters=filters)
            print(f"Vector search returned {len(retrieved)} chunks")
        except Exception as e:
            print(f"Vector search completely failed: {str(e)}")
            # If vector search fails but documents exist, get chunks from latest document only
            if chunk_count > 0:
                try:
                    db.rollback()  # Clean transaction state
                    # Get latest document ID first
                    latest_doc_result = db.execute(text("""
                        SELECT id::text FROM documents 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """)).fetchone()
                    if latest_doc_result:
                        latest_doc_id = latest_doc_result[0]
                        fallback_result = db.execute(text("""
                            SELECT id::text, 1.0 AS score 
                            FROM chunks 
                            WHERE doc_id = :latest_doc_id
                            ORDER BY created_at DESC 
                            LIMIT :k
                        """), {"latest_doc_id": latest_doc_id, "k": 8}).all()
                        retrieved = [(r[0], float(r[1])) for r in fallback_result]
                        print(f"Using direct chunk retrieval: {len(retrieved)} chunks from latest document")
                    else:
                        retrieved = []
                except Exception as e2:
                    print(f"Direct chunk retrieval also failed: {str(e2)}")
                    retrieved = []
        
        # If vector search returned empty but chunks exist, use fallback
        if not retrieved and chunk_count > 0:
            print(f"Vector search returned empty, but {chunk_count} chunks exist. Using fallback retrieval.")
            try:
                db.rollback()
                # Get latest document ID first
                latest_doc_result = db.execute(text("""
                    SELECT id::text FROM documents 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """)).fetchone()
                if latest_doc_result:
                    latest_doc_id = latest_doc_result[0]
                    fallback_result = db.execute(text("""
                        SELECT id::text, 1.0 AS score 
                        FROM chunks 
                        WHERE doc_id = :latest_doc_id
                        ORDER BY created_at DESC 
                        LIMIT :k
                    """), {"latest_doc_id": latest_doc_id, "k": 10}).all()
                    retrieved = [(r[0], float(r[1])) for r in fallback_result]
                    print(f"Fallback retrieval returned {len(retrieved)} chunks from latest document")
                else:
                    retrieved = []
            except Exception as e:
                print(f"Fallback retrieval failed: {str(e)}")
                retrieved = []

        # Check if we have any retrieved chunks
        if not retrieved:
            processing_prefix = ""
            if chunk_count == 0:
                doc_count = db.execute(text("SELECT COUNT(*) FROM documents")).scalar() or 0
                if doc_count > 0:
                    processing_prefix = "Your documents are still being processed, but here's what I can share right now:\n\n"
            
            answer_html, general_citations = _generate_general_answer_with_sources(question)
            if processing_prefix and answer_html:
                answer_html = f"{processing_prefix}{answer_html}"
            
            followups = [
                "Ask another question",
                "Upload documents for precise answers",
                "Check document status" if processing_prefix else "Learn about SRM University"
            ]
            followups = [f for f in followups if isinstance(f, str)]
            
            return AskResponse(
                answer_html=answer_html,
                citations=general_citations,
                followups=followups,
                query_rewrite=query_rewrite,
                safety_notes="",
            )

        # Rerank via MMR
        reranked = mmr_rerank(retrieved, top_k=5)

        # Get chunk content for context
        chunk_contents = []
        citations: List[Citation] = []
        
        for chunk_id, score in reranked:
            try:
                # Get chunk content from database
                result = db.execute(text("""
                    SELECT c.content, c.page_no, d.title, d.source_type
                    FROM chunks c
                    JOIN documents d ON c.doc_id = d.id
                    WHERE c.id = :chunk_id
                """), {"chunk_id": chunk_id}).fetchone()
                
                if result:
                    content, page_no, title, source_type = result
                    chunk_contents.append(content)
                    citations.append(Citation(
                        title=title or "Document",
                        url=None,
                        source_type=source_type or "document",
                        page=page_no,
                        chunk_id=chunk_id
                    ))
            except Exception as e:
                print(f"Error retrieving chunk {chunk_id}: {str(e)}")
                continue

        # Generate answer based on retrieved content (only if the user explicitly asked about documents)
        if needs_doc_context and chunk_contents and _has_relevant_context(question, chunk_contents):
            answer_html = _generate_answer(question, chunk_contents)
            followups = _generate_followups(question, chunk_contents)
        else:
            answer_html, general_citations = _generate_general_answer_with_sources(question)
            citations = general_citations
            followups = ["Ask another question", "Upload more documents", "Check document status"]

        return AskResponse(
            answer_html=answer_html,
            citations=citations,
            followups=followups,
            query_rewrite=query_rewrite,
            safety_notes="",
        )

    except Exception as e:
        print(f"Error in RAG pipeline: {str(e)}")
        return AskResponse(
            answer_html="I encountered an error processing your question. Please try again.",
            citations=[],
            followups=["Try rephrasing your question", "Upload more documents"],
            query_rewrite=question,
            safety_notes="",
        )


def _generate_answer(question: str, chunk_contents: List[str]) -> str:
    """Generate an answer using LLM with document context."""
    # Combine document chunks into context
    context = "\n\n---\n\n".join(chunk_contents[:5])  # Use top 5 chunks for better context
    
    # Check if LLM is available
    if not is_llm_available():
        # Fallback to simple answer if no LLM
        return f"Based on the uploaded documents, here's what I found:\n\n{context[:1000]}..."
    
    # Create a system prompt that instructs the LLM to use document context
    system_prompt = """You are SRM UniChat, a helpful AI assistant. Answer the user's question using the provided document context.

IMPORTANT INSTRUCTIONS:
1. Use the document context provided below to answer the question accurately.
2. You can also use your general knowledge to enhance the answer, but prioritize information from the documents.
3. If the document context is relevant, base your answer primarily on it.
4. When the context does not fully cover the question, fill the gaps with reliable general knowledge without stating or implying that the documents are missing information.
5. Be clear, concise, and helpful.
6. Do NOT use HTML tags like <p>, <strong>, etc. Use plain text only.
7. If you reference the document context directly, cite it naturally in your response using brief parenthetical notes.
8. Never mention the uploaded document titles, authors, or that the content comes from a resume unless the user explicitly asked about the document itself.

Document Context:
{context}

Now answer the user's question based on the context above.""".format(context=context[:4000])  # Limit context to avoid token limits
    
    try:
        answer_text = get_llm_response(question, system_prompt)
        if answer_text:
            return answer_text
        else:
            # Fallback if LLM fails
            return f"Based on the uploaded documents, here's what I found:\n\n{context[:1000]}..."
    except Exception as e:
        print(f"Error generating answer with LLM: {str(e)}")
        # Fallback to simple answer
        return f"Based on the uploaded documents, here's what I found:\n\n{context[:1000]}..."


def _generate_followups(question: str, chunk_contents: List[str]) -> List[str]:
    """Generate follow-up questions based on the content."""
    followups = []
    
    if "srm" in question.lower():
        followups.extend([
            "Tell me about SRM University campuses",
            "What programs does SRM University offer?",
            "How can I apply to SRM University?"
        ])
    else:
        followups.extend([
            "Tell me more about this topic",
            "What other information is available?",
            "Can you provide more details?"
        ])
    
    return followups[:3]  # Return max 3 followups


def _tokenize_text(text: str, min_len: int = 3) -> set[str]:
    """Convert text to a set of lowercase keyword tokens."""
    if not text:
        return set()
    pattern = rf"[a-zA-Z0-9]{{{min_len},}}"
    tokens = re.findall(pattern, text.lower())
    return set(tokens)


def _extract_question_tokens(question: str) -> set[str]:
    """
    Extract meaningful tokens from the user question, avoiding generic words.
    Keeps acronyms like 'srm' but filters common verbs and interrogatives.
    """
    tokens = _tokenize_text(question, min_len=2)
    important: set[str] = set()
    for token in tokens:
        if token in QUESTION_STOPWORDS:
            continue
        if len(token) < 4 and token not in {"srm", "srmap", "ap"}:
            continue
        important.add(token)
    return important


def _has_relevant_context(question: str, chunk_contents: List[str], threshold: float = 0.25) -> bool:
    """
    Simple heuristic to decide if retrieved chunks overlap with the user question.
    Prevents citing uploaded PDFs when the content likely does not answer the query.
    """
    question_tokens = _extract_question_tokens(question)
    if not question_tokens:
        return False
    
    context_tokens: set[str] = set()
    for content in chunk_contents:
        context_tokens.update(_tokenize_text(content))
    
    if not context_tokens:
        return False
    
    overlap = question_tokens & context_tokens
    if not overlap:
        return False
    
    # Require at least two overlapping keywords for broader questions
    if len(question_tokens) >= 3 and len(overlap) < 2:
        return False
    
    ratio = len(overlap) / len(question_tokens)
    return ratio >= threshold or len(overlap) >= 3


def _needs_document_context(question: str) -> bool:
    """Detect whether the user explicitly wants information from the uploaded documents."""
    if not question:
        return False
    lowered = question.lower()
    keywords = [
        "document",
        "pdf",
        "file",
        "resume",
        "cv",
        "page",
        "chunk",
        "upload",
        "in the doc",
        "from the doc",
        "according to the doc",
        "in the pdf",
        "from the pdf",
        "this resume",
        "that resume",
        "above document",
        "uploaded",
    ]
    return any(keyword in lowered for keyword in keywords)


def _default_llm_citation() -> Citation:
    """Return a default citation pointing to the SRM University AP official website."""
    return Citation(
        title="SRM University AP (Official)",
        url="https://srmap.edu.in",
        source_type="web",
        page=None,
        chunk_id=None,
    )


def _extract_json_dict(raw: str) -> Dict[str, Any] | None:
    """Attempt to parse a JSON object from an LLM response."""
    if not raw:
        return None
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = cleaned[start : end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                return None
    return None


def _generate_general_answer_with_sources(question: str) -> Tuple[str, List[Citation]]:
    """
    Use the configured LLM to produce an answer plus at least one source citation.
    Falls back to default messaging if no LLM is available or if parsing fails.
    """
    if not is_llm_available():
        return (
            "No AI API key is configured. Please add your GEMINI_API_KEY (free) or OPENAI_API_KEY to the .env file and restart the backend.",
            [],
        )
    
    instruction = """You are SRM UniChat, a friendly and factual assistant.
Respond using only reliable public web information, prioritizing official SRM University AP (SRMAP) websites or trusted Google search results.
Return a valid JSON object that follows this schema exactly:
{
  "answer": "Plain text answer without HTML",
  "sources": [
    { "title": "Source title", "url": "https://example.com" }
  ]
}

Requirements:
- Always provide your best possible answer, even if no documents are available.
- Include at least two public website URLs (prefer srmap.edu.in or other reputable SRM AP resources). Do not cite uploaded documents or internal knowledge bases.
- Do not include Markdown code fences or any keys beyond answer and sources."""
    
    fallback_text = "I'm having trouble connecting to the AI service right now. Please try again in a moment."
    
    try:
        raw_response = get_llm_response(question, instruction)
    except Exception as e:
        return (str(e), [])
    
    if not raw_response:
        return (fallback_text, [_default_llm_citation()])
    
    parsed = _extract_json_dict(raw_response)
    if not parsed:
        answer = raw_response.strip() or fallback_text
        return (answer, [_default_llm_citation()])
    
    answer_text = str(parsed.get("answer") or "").strip()
    sources = parsed.get("sources") or []
    
    citations: List[Citation] = []
    if isinstance(sources, list):
        for src in sources:
            if not isinstance(src, dict):
                continue
            title = (src.get("title") or "Source").strip() or "Source"
            url = src.get("url")
            citations.append(
                Citation(
                    title=title,
                    url=url,
                    source_type="web",
                    page=None,
                    chunk_id=None,
                )
            )
    
    if not answer_text:
        answer_text = fallback_text
    if not citations:
        citations = [_default_llm_citation()]
    
    return answer_text, citations



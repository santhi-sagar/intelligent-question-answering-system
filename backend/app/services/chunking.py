from typing import List, Tuple
import tiktoken


def chunk_text(pages: List[Tuple[int, str]], max_tokens: int = 1000, overlap: int = 150) -> List[Tuple[int, str]]:
    """Token-aware text chunking using tiktoken for accurate token counting."""
    chunks: List[Tuple[int, str]] = []
    
    # Initialize tokenizer
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
    except Exception:
        # Fallback to character-based chunking if tiktoken fails
        print("Warning: tiktoken not available, using character-based chunking")
        return _chunk_text_fallback(pages, max_tokens, overlap)
    
    for page_no, text in pages:
        if not text.strip():
            continue
            
        # Split text into sentences for better chunking
        sentences = _split_into_sentences(text)
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(encoding.encode(sentence))
            
            # If adding this sentence would exceed max_tokens, save current chunk
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                chunks.append((page_no, current_chunk.strip()))
                current_chunk = sentence
                current_tokens = sentence_tokens
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append((page_no, current_chunk.strip()))
    
    # Apply overlap between chunks
    if overlap > 0 and len(chunks) > 1:
        chunks = _apply_overlap(chunks, overlap, encoding)
    
    return chunks


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences for better chunking."""
    import re
    # Simple sentence splitting - can be improved with more sophisticated NLP
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def _apply_overlap(chunks: List[Tuple[int, str]], overlap_tokens: int, encoding) -> List[Tuple[int, str]]:
    """Apply overlap between chunks to maintain context."""
    if len(chunks) <= 1:
        return chunks
    
    overlapped_chunks = []
    
    for i, (page_no, chunk_text) in enumerate(chunks):
        if i == 0:
            overlapped_chunks.append((page_no, chunk_text))
            continue
        
        # Get the end of the previous chunk for overlap
        prev_chunk = overlapped_chunks[-1][1]
        prev_tokens = encoding.encode(prev_chunk)
        
        # Take the last overlap_tokens from previous chunk
        if len(prev_tokens) > overlap_tokens:
            overlap_text = encoding.decode(prev_tokens[-overlap_tokens:])
            overlapped_chunk = overlap_text + " " + chunk_text
        else:
            overlapped_chunk = prev_chunk + " " + chunk_text
        
        overlapped_chunks.append((page_no, overlapped_chunk))
    
    return overlapped_chunks


def _chunk_text_fallback(pages: List[Tuple[int, str]], max_tokens: int = 1000, overlap: int = 150) -> List[Tuple[int, str]]:
    """Fallback character-based chunking when tiktoken is not available."""
    chunks: List[Tuple[int, str]] = []
    approx_chars = max_tokens * 4  # Rough approximation: 4 chars per token
    
    for page_no, text in pages:
        start = 0
        while start < len(text):
            end = min(len(text), start + approx_chars)
            chunks.append((page_no, text[start:end]))
            if end == len(text):
                break
            start = max(0, end - overlap * 4)
    
    return chunks



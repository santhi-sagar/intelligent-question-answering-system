from typing import List
import hashlib
import random
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from ..config import settings


client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def create_fallback_embedding(text: str, dimension: int = 1536) -> List[float]:
    """Create a deterministic fallback embedding based on text content."""
    # Use text hash to create deterministic but varied embeddings
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Convert hash to numbers and create embedding-like vector
    embedding = []
    for i in range(0, len(text_hash), 2):
        hex_pair = text_hash[i:i+2]
        value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
        embedding.append(value)
    
    # Pad or truncate to desired dimension
    while len(embedding) < dimension:
        embedding.append(embedding[len(embedding) % len(embedding)])
    
    return embedding[:dimension]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for texts, with fallback for rate limiting."""
    if not texts:
        return []
    
    # If no OpenAI client, use fallback
    if client is None:
        print("No OpenAI API key, using fallback embeddings")
        return [create_fallback_embedding(text) for text in texts]
    
    try:
        model = settings.embedding_model if settings.embedding_model != "auto" else "text-embedding-3-small"
        resp = client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in resp.data]
    except Exception as e:
        print(f"OpenAI API error: {str(e)}, using fallback embeddings")
        return [create_fallback_embedding(text) for text in texts]



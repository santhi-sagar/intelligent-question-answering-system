"""LLM client for OpenAI and Google Gemini."""
import os
from typing import Optional
from ..config import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def is_llm_available() -> bool:
    """Check if any LLM API key is configured."""
    return bool(settings.gemini_api_key) or bool(settings.openai_api_key)

def get_llm_response(question: str, system_prompt: str) -> Optional[str]:
    """
    Get LLM response from either Gemini or OpenAI.
    Tries Gemini first (free tier), then falls back to OpenAI.
    Returns None if both fail (but not due to missing API keys).
    """
    # Try Gemini first (free tier)
    if settings.gemini_api_key:
        try:
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai package not installed")
            
            genai.configure(api_key=settings.gemini_api_key)
            model_name = settings.gemini_model or "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name)
            
            # Combine system prompt and question
            prompt = f"{system_prompt}\n\nUser: {question}\n\nAssistant:"
            
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            error_msg = str(e).lower()
            # If it's an API key error, raise it so the caller can handle it
            if "api key" in error_msg or "api_key" in error_msg or "invalid" in error_msg:
                raise Exception(f"Gemini API key error: {str(e)}")
            # Otherwise, log and try OpenAI
            print(f"Gemini API error: {str(e)}, trying OpenAI...")
    
    # Fall back to OpenAI
    if settings.openai_api_key:
        try:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed")
            
            client = OpenAI(api_key=settings.openai_api_key)
            
            # Determine model
            if settings.openai_model == "auto":
                model = "gpt-3.5-turbo"
            else:
                model = settings.openai_model
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e).lower()
            # If it's an API key error, raise it
            if "api key" in error_msg or "api_key" in error_msg or "invalid" in error_msg or "unauthorized" in error_msg:
                raise Exception(f"OpenAI API key error: {str(e)}")
            # Otherwise, return None to indicate temporary failure
            print(f"OpenAI API error: {str(e)}")
    
    # If we get here, both APIs failed (but not due to API key errors)
    return None


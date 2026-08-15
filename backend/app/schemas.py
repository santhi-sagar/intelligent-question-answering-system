from pydantic import BaseModel, AnyUrl, Field
from typing import List, Optional
from uuid import UUID


class DocumentCreate(BaseModel):
    title: Optional[str] = None
    source_url: Optional[AnyUrl] = None
    source_type: Optional[str] = None
    metadata: Optional[dict] = None


class DocumentOut(BaseModel):
    id: UUID
    title: Optional[str]
    source_url: Optional[str]
    source_type: Optional[str]

    class Config:
        from_attributes = True


class ChunkOut(BaseModel):
    id: UUID
    doc_id: UUID
    content: str
    page_no: Optional[int]
    token_count: Optional[int]

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    chunk: ChunkOut
    score: float
    metadata: dict | None = None


class AskRequest(BaseModel):
    question: str
    filters: Optional[dict] = None


class Citation(BaseModel):
    title: str
    url: Optional[str]
    source_type: str
    page: Optional[int]
    chunk_id: Optional[str]


class AskResponse(BaseModel):
    answer_html: str
    citations: List[Citation]
    followups: List[str]
    query_rewrite: str
    safety_notes: str


class LoginRequest(BaseModel):
    roll_no: str = Field(..., min_length=1, description="Student roll number")
    dob: str = Field(..., description="Date of birth in YYYY-MM-DD format")


class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    roll_no: Optional[str] = None



from typing import Dict


def build_citation(title: str | None, url: str | None, source_type: str, page: int | None, chunk_id: str) -> Dict:
    return {
        "title": title or "Source",
        "url": url,
        "source_type": source_type,
        "page": page,
        "chunk_id": chunk_id,
    }



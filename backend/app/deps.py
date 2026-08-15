from fastapi import Header, HTTPException


def rate_limit_placeholder(x_forwarded_for: str | None = Header(default=None)) -> None:
    # Simple placeholder for rate limiting; can be expanded later.
    # Reject obviously malformed IP headers to avoid header injection.
    if x_forwarded_for is not None and "\n" in x_forwarded_for:
        raise HTTPException(status_code=400, detail="Invalid header")



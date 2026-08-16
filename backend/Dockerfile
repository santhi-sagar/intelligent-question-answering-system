FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

    WORKDIR /app

    # System deps for psycopg and pandas
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl libpq-dev gcc \
         && rm -rf /var/lib/apt/lists/*

         # Python deps (no poetry)
         COPY requirements.txt /tmp/requirements.txt
         RUN pip install --no-cache-dir -r /tmp/requirements.txt

         # App code
         COPY . /app

         EXPOSE 8000
         # Initialize the pgvector schema before starting the API.
         CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
         

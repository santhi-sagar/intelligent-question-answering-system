# backend/app/db.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
# remove this if you have it here (we don't want NullPool for the app engine):
# from sqlalchemy.pool import NullPool
from .config import settings
try:
    # Register pgvector adapter for psycopg so Python lists bind to vector columns
    from pgvector.psycopg import register_vector  # type: ignore
except Exception:  # pragma: no cover
    register_vector = None  # fallback when library missing

engine = create_engine(
    settings.database_url,       # e.g. postgresql+psycopg://postgres:***@db:5432/srm
    pool_pre_ping=True,          # <- important: auto-recycle dead connections
    pool_recycle=1800,           # recycle connections after 30 minutes (tune as you like)
    connect_args={               # optional niceties for psycopg/libpq
        "connect_timeout": 5,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
)

# Ensure pgvector adapter is registered on each new DBAPI connection
if register_vector is not None:
    @event.listens_for(engine, "connect")
    def _register_vector_adapter(dbapi_connection, connection_record):  # type: ignore
        try:
            register_vector(dbapi_connection)
        except Exception:
            # Non-fatal; queries will still work but vector ops may fail
            pass

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

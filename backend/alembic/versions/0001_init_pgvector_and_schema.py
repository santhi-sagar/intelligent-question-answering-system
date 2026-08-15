"""init pgvector and schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS documents (
              id uuid PRIMARY KEY,
              title text,
              source_url text,
              source_type text CHECK (source_type IN ('pdf','docx','web','xlsx','csv','txt')),
              doc_metadata jsonb,
              created_at timestamptz DEFAULT now(),
              updated_at timestamptz DEFAULT now()
            );
            
            CREATE TABLE IF NOT EXISTS chunks (
              id uuid PRIMARY KEY,
              doc_id uuid REFERENCES documents(id) ON DELETE CASCADE,
              content text NOT NULL,
              page_no int,
              token_count int,
              embedding vector(1536) NOT NULL,
              created_at timestamptz DEFAULT now()
            );

            CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
            CREATE INDEX IF NOT EXISTS idx_chunks_page_no ON chunks(page_no);
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);

            CREATE TABLE IF NOT EXISTS fees (
              program text,
              level text,
              year text,
              campus text,
              amount numeric,
              currency text,
              updated_at timestamptz,
              source_url text
            );

            CREATE TABLE IF NOT EXISTS deadlines (
              category text,
              name text,
              date date,
              campus text,
              program text,
              updated_at timestamptz,
              source_url text
            );

            CREATE TABLE IF NOT EXISTS departments (
              name text,
              campus text,
              email text,
              phone text,
              office_hours text,
              updated_at timestamptz,
              source_url text
            );

            CREATE TABLE IF NOT EXISTS contacts (
              role text,
              name text,
              email text,
              phone text,
              campus text,
              updated_at timestamptz,
              source_url text
            );

            CREATE INDEX IF NOT EXISTS idx_fees_keys ON fees(program, level, year, campus);
            CREATE INDEX IF NOT EXISTS idx_deadlines_keys ON deadlines(category, name, campus, program);
            CREATE INDEX IF NOT EXISTS idx_departments_keys ON departments(name, campus);
            CREATE INDEX IF NOT EXISTS idx_contacts_keys ON contacts(role, campus);
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DROP TABLE IF EXISTS contacts;
            DROP TABLE IF EXISTS departments;
            DROP TABLE IF EXISTS deadlines;
            DROP TABLE IF EXISTS fees;
            DROP TABLE IF EXISTS chunks;
            DROP TABLE IF EXISTS documents;
            """
        )
    )



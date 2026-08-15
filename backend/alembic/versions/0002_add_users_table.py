"""add users table

Revision ID: 0002
Revises: 0001
Create Date: 2024-12-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS users (
              id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
              roll_no text NOT NULL UNIQUE,
              dob text NOT NULL,
              created_at timestamptz DEFAULT now(),
              updated_at timestamptz DEFAULT now()
            );
            
            CREATE INDEX IF NOT EXISTS idx_users_roll_no ON users(roll_no);
            """
        )
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_users_roll_no;")
    op.execute("DROP TABLE IF EXISTS users;")


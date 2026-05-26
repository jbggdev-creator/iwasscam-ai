"""add rag_documents table with pgvector

Revision ID: a4f8e2b91c3d
Revises: 3185515645c2
Create Date: 2026-05-25 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a4f8e2b91c3d"
down_revision: Union[str, None] = "3185515645c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_EMBEDDING_DIM = 384  # BAAI/bge-small-en-v1.5


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "rag_documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        # Raw SQL type string — pgvector's Vector is not natively understood by Alembic
        sa.Column("embedding", sa.Text().with_variant(sa.Text(), "postgresql"), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # Replace the text column with the correct vector type
    op.execute(f"ALTER TABLE rag_documents ALTER COLUMN embedding TYPE vector({_EMBEDDING_DIM}) USING NULL")
    op.create_index("ix_rag_documents_source", "rag_documents", ["source"])
    # IVFFlat index for approximate nearest-neighbour cosine search
    op.execute(
        "CREATE INDEX ix_rag_documents_embedding "
        "ON rag_documents USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 10)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_rag_documents_embedding")
    op.drop_index("ix_rag_documents_source", table_name="rag_documents")
    op.drop_table("rag_documents")

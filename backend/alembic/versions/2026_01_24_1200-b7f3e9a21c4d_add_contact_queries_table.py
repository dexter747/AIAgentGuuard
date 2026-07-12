"""add_contact_queries_table

Revision ID: b7f3e9a21c4d
Revises: a5a6762b605c
Create Date: 2026-01-24 12:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'b7f3e9a21c4d'
down_revision: Union[str, None] = 'a5a6762b605c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'contact_queries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_contact_queries_email', 'contact_queries', ['email'])
    op.create_index('ix_contact_queries_is_read', 'contact_queries', ['is_read'])
    op.create_index('ix_contact_queries_created_at', 'contact_queries', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_contact_queries_created_at', 'contact_queries')
    op.drop_index('ix_contact_queries_is_read', 'contact_queries')
    op.drop_index('ix_contact_queries_email', 'contact_queries')
    op.drop_table('contact_queries')

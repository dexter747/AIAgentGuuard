"""add_webhooks_table

Revision ID: cc21d3974533
Revises: f18fcdb5ea1e
Create Date: 2026-01-24 06:06:52.031772+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc21d3974533'
down_revision: Union[str, None] = 'f18fcdb5ea1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'webhooks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('events', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('secret', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_webhooks_org_id'), 'webhooks', ['org_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_webhooks_org_id'), table_name='webhooks')
    op.drop_table('webhooks')

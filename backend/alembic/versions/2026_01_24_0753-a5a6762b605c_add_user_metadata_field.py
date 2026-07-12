"""add_user_metadata_field

Revision ID: a5a6762b605c
Revises: cc21d3974533
Create Date: 2026-01-24 07:53:00.767613+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = 'a5a6762b605c'
down_revision: Union[str, None] = 'cc21d3974533'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('user_metadata', JSON, nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'user_metadata')

"""add_missing_fields_to_users_and_health_checks

Revision ID: 574ec3d63325
Revises: c76dd9743a7b
Create Date: 2026-01-23 16:52:47.523305+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '574ec3d63325'
down_revision: Union[str, None] = 'c76dd9743a7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing fields to users table
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('email_verification_token', sa.String(255), nullable=True))
    
    # Add missing fields to health_checks table
    op.add_column('health_checks', sa.Column('endpoint', sa.String(500), nullable=True))
    op.add_column('health_checks', sa.Column('interval_minutes', sa.Integer(), server_default='5', nullable=False))
    op.add_column('health_checks', sa.Column('timeout_seconds', sa.Integer(), server_default='30', nullable=False))
    op.add_column('health_checks', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('health_checks', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('health_checks', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    
    # Create index on is_active for better query performance
    op.create_index('ix_health_checks_is_active', 'health_checks', ['is_active'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_health_checks_is_active', 'health_checks')
    
    # Remove fields from health_checks
    op.drop_column('health_checks', 'updated_at')
    op.drop_column('health_checks', 'created_at')
    op.drop_column('health_checks', 'is_active')
    op.drop_column('health_checks', 'timeout_seconds')
    op.drop_column('health_checks', 'interval_minutes')
    op.drop_column('health_checks', 'endpoint')
    
    # Remove fields from users
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified')


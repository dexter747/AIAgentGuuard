"""Add performance indexes

Revision ID: add_performance_indexes
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = '574ec3d63325'  # add_missing_fields_to_users_and_health
branch_labels = None
depends_on = None


def upgrade():
    # Traces table indexes for common queries
    op.create_index(
        'ix_traces_agent_id_created_at',
        'traces',
        ['agent_id', 'created_at'],
        unique=False
    )
    op.create_index(
        'ix_traces_status',
        'traces',
        ['status'],
        unique=False
    )
    
    # Health checks table indexes
    op.create_index(
        'ix_health_checks_agent_id_checked_at',
        'health_checks',
        ['agent_id', 'checked_at'],
        unique=False
    )
    op.create_index(
        'ix_health_checks_status',
        'health_checks',
        ['status'],
        unique=False
    )
    
    # Agents table indexes (using org_id, not organization_id)
    op.create_index(
        'ix_agents_org_id_created_at',
        'agents',
        ['org_id', 'created_at'],
        unique=False
    )


def downgrade():
    op.drop_index('ix_agents_org_id_created_at', table_name='agents')
    op.drop_index('ix_health_checks_status', table_name='health_checks')
    op.drop_index('ix_health_checks_agent_id_checked_at', table_name='health_checks')
    op.drop_index('ix_traces_status', table_name='traces')
    op.drop_index('ix_traces_agent_id_created_at', table_name='traces')

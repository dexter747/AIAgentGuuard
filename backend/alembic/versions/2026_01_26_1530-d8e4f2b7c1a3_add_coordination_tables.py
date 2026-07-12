"""Add coordination intelligence tables for Phase 2

Revision ID: d8e4f2b7c1a3
Revises: b7f3e9a21c4d
Create Date: 2026-01-26 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd8e4f2b7c1a3'
down_revision: Union[str, None] = 'b7f3e9a21c4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create coordination_issues table
    op.create_table(
        'coordination_issues',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('trace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('traces.id'), nullable=True),
        sa.Column('issue_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, default='medium'),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('affected_agents', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('evidence', postgresql.JSONB(), nullable=True),
        sa.Column('context', postgresql.JSONB(), nullable=True),
        sa.Column('suggested_fix', sa.Text(), nullable=True),
        sa.Column('fix_confidence', sa.Float(), nullable=True),
        sa.Column('user_feedback', sa.String(20), default='pending'),
        sa.Column('feedback_comment', sa.Text(), nullable=True),
        sa.Column('feedback_at', sa.DateTime(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), default=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_coordination_issues_org_id', 'coordination_issues', ['org_id'])
    op.create_index('ix_coordination_issues_trace_id', 'coordination_issues', ['trace_id'])
    op.create_index('ix_coordination_issues_issue_type', 'coordination_issues', ['issue_type'])
    op.create_index('ix_coordination_issues_severity', 'coordination_issues', ['severity'])
    op.create_index('ix_coordination_issues_detected_at', 'coordination_issues', ['detected_at'])

    # Create corrective_suggestions table
    op.create_table(
        'corrective_suggestions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('issue_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('coordination_issues.id'), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('correction_strategy', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('original_flow', postgresql.JSONB(), nullable=False),
        sa.Column('corrected_flow', postgresql.JSONB(), nullable=False),
        sa.Column('changes', postgresql.JSONB(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, default=0.5),
        sa.Column('is_ml_generated', sa.Boolean(), default=False),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('applied', sa.Boolean(), default=False),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_corrective_suggestions_issue_id', 'corrective_suggestions', ['issue_id'])
    op.create_index('ix_corrective_suggestions_org_id', 'corrective_suggestions', ['org_id'])

    # Create learned_patterns table
    op.create_table(
        'learned_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('pattern_name', sa.String(255), nullable=False),
        sa.Column('pattern_signature', postgresql.JSONB(), nullable=False),
        sa.Column('correction_template', postgresql.JSONB(), nullable=False),
        sa.Column('times_applied', sa.Integer(), default=0),
        sa.Column('success_rate', sa.Float(), default=0.0),
        sa.Column('last_applied_at', sa.DateTime(), nullable=True),
        sa.Column('source_suggestion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('corrective_suggestions.id'), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_learned_patterns_org_id', 'learned_patterns', ['org_id'])
    op.create_index('ix_learned_patterns_pattern_type', 'learned_patterns', ['pattern_type'])

    # Create agent_handoffs table
    op.create_table(
        'agent_handoffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('trace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('traces.id'), nullable=True),
        sa.Column('from_agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('to_agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('task_type', sa.String(100), nullable=True),
        sa.Column('task_data', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_type', sa.String(100), nullable=True),
        sa.Column('sender_state', postgresql.JSONB(), nullable=True),
        sa.Column('receiver_state', postgresql.JSONB(), nullable=True),
        sa.Column('state_drift_detected', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_agent_handoffs_org_id', 'agent_handoffs', ['org_id'])
    op.create_index('ix_agent_handoffs_trace_id', 'agent_handoffs', ['trace_id'])
    op.create_index('ix_agent_handoffs_from_agent_id', 'agent_handoffs', ['from_agent_id'])
    op.create_index('ix_agent_handoffs_to_agent_id', 'agent_handoffs', ['to_agent_id'])

    # Create coordination_metrics table
    op.create_table(
        'coordination_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_issues', sa.Integer(), default=0),
        sa.Column('critical_issues', sa.Integer(), default=0),
        sa.Column('high_issues', sa.Integer(), default=0),
        sa.Column('medium_issues', sa.Integer(), default=0),
        sa.Column('low_issues', sa.Integer(), default=0),
        sa.Column('state_drift_count', sa.Integer(), default=0),
        sa.Column('handoff_failure_count', sa.Integer(), default=0),
        sa.Column('broken_assumption_count', sa.Integer(), default=0),
        sa.Column('duplicate_work_count', sa.Integer(), default=0),
        sa.Column('circular_dependency_count', sa.Integer(), default=0),
        sa.Column('resolved_issues', sa.Integer(), default=0),
        sa.Column('avg_resolution_time_ms', sa.Integer(), nullable=True),
        sa.Column('total_handoffs', sa.Integer(), default=0),
        sa.Column('successful_handoffs', sa.Integer(), default=0),
        sa.Column('failed_handoffs', sa.Integer(), default=0),
        sa.Column('handoff_success_rate', sa.Float(), nullable=True),
        sa.Column('avg_handoff_duration_ms', sa.Integer(), nullable=True),
        sa.Column('suggestions_generated', sa.Integer(), default=0),
        sa.Column('suggestions_approved', sa.Integer(), default=0),
        sa.Column('suggestions_rejected', sa.Integer(), default=0),
        sa.Column('suggestion_approval_rate', sa.Float(), nullable=True),
        sa.Column('computed_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_coordination_metrics_org_id', 'coordination_metrics', ['org_id'])
    op.create_index('ix_coordination_metrics_agent_id', 'coordination_metrics', ['agent_id'])
    op.create_index('ix_coordination_metrics_period_start', 'coordination_metrics', ['period_start'])


def downgrade() -> None:
    op.drop_table('coordination_metrics')
    op.drop_table('agent_handoffs')
    op.drop_table('learned_patterns')
    op.drop_table('corrective_suggestions')
    op.drop_table('coordination_issues')

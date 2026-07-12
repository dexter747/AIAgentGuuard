# Analytics background tasks
from app.core.celery_app import celery_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def generate_daily_report():
    """Generate daily analytics report for all organizations"""
    from app.core.database import SessionLocal
    from app.models.organization import Organization
    
    logger.info("Starting daily analytics report generation")
    
    db = SessionLocal()
    try:
        orgs = db.query(Organization).filter(Organization.is_active == True).all()
        
        for org in orgs:
            calculate_org_daily_stats.delay(org.id)
        
        logger.info(f"Queued daily reports for {len(orgs)} organizations")
    finally:
        db.close()


@celery_app.task
def calculate_org_daily_stats(org_id: int):
    """Calculate daily statistics for a single organization"""
    from app.core.database import SessionLocal
    from app.models.trace import Trace
    from app.models.test import Test, TestRun
    from app.models.agent import Agent
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)
        today = datetime.utcnow()
        
        # Calculate trace stats
        trace_stats = db.query(
            func.count(Trace.id).label('total'),
            func.sum(case((Trace.status == 'success', 1), else_=0)).label('success'),
            func.sum(case((Trace.status == 'error', 1), else_=0)).label('errors'),
            func.avg(Trace.duration_ms).label('avg_duration'),
            func.sum(Trace.total_cost).label('total_cost'),
            func.sum(Trace.total_tokens).label('total_tokens')
        ).filter(
            Trace.org_id == org_id,
            Trace.created_at >= yesterday,
            Trace.created_at < today
        ).first()
        
        # Calculate test stats
        test_stats = db.query(
            func.count(TestRun.id).label('total_runs'),
            func.sum(case((TestRun.status == 'passed', 1), else_=0)).label('passed'),
            func.sum(case((TestRun.status == 'failed', 1), else_=0)).label('failed')
        ).join(Test).filter(
            Test.org_id == org_id,
            TestRun.started_at >= yesterday,
            TestRun.started_at < today
        ).first()
        
        # Calculate agent health
        agent_stats = db.query(
            func.count(Agent.id).label('total'),
            func.sum(case((Agent.health_status == 'healthy', 1), else_=0)).label('healthy'),
            func.sum(case((Agent.health_status == 'degraded', 1), else_=0)).label('degraded'),
            func.sum(case((Agent.health_status == 'failing', 1), else_=0)).label('failing')
        ).filter(Agent.org_id == org_id).first()
        
        # Store in Redis or a stats table for quick access
        stats = {
            "date": yesterday.strftime("%Y-%m-%d"),
            "org_id": org_id,
            "traces": {
                "total": trace_stats.total or 0,
                "success": trace_stats.success or 0,
                "errors": trace_stats.errors or 0,
                "avg_duration_ms": float(trace_stats.avg_duration or 0),
                "total_cost": float(trace_stats.total_cost or 0),
                "total_tokens": trace_stats.total_tokens or 0
            },
            "tests": {
                "total_runs": test_stats.total_runs or 0,
                "passed": test_stats.passed or 0,
                "failed": test_stats.failed or 0
            },
            "agents": {
                "total": agent_stats.total or 0,
                "healthy": agent_stats.healthy or 0,
                "degraded": agent_stats.degraded or 0,
                "failing": agent_stats.failing or 0
            }
        }
        
        logger.info(f"Generated daily stats for org {org_id}: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to calculate stats for org {org_id}: {str(e)}")
        raise
    finally:
        db.close()


# Import case for SQLAlchemy queries
from sqlalchemy import case


@celery_app.task
def calculate_cost_savings(org_id: int, period_days: int = 30):
    """Calculate how much money the organization saved using mocks vs real APIs"""
    from app.core.database import SessionLocal
    from app.models.trace import Trace
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        
        # Get test runs that used mocks
        # This is a simplified calculation
        # In reality, you'd track mock usage separately
        
        mock_trace_count = db.query(func.count(Trace.id)).filter(
            Trace.org_id == org_id,
            Trace.created_at >= cutoff,
            Trace.is_mock == True  # Assuming this field exists
        ).scalar() or 0
        
        # Estimate cost per real API call
        avg_cost_per_trace = 0.55  # Based on whitepaper estimate
        
        estimated_savings = mock_trace_count * avg_cost_per_trace
        
        return {
            "org_id": org_id,
            "period_days": period_days,
            "mock_trace_count": mock_trace_count,
            "estimated_savings_usd": estimated_savings
        }
    finally:
        db.close()


@celery_app.task
def generate_usage_report(org_id: int, start_date: str, end_date: str):
    """Generate a usage report for billing purposes"""
    from app.core.database import SessionLocal
    from app.models.trace import Trace
    from app.models.test import TestRun
    from sqlalchemy import func
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    db = SessionLocal()
    try:
        # Count traces
        trace_count = db.query(func.count(Trace.id)).filter(
            Trace.org_id == org_id,
            Trace.created_at >= start,
            Trace.created_at < end
        ).scalar() or 0
        
        # Count test runs
        test_run_count = db.query(func.count(TestRun.id)).join(Test).filter(
            Test.org_id == org_id,
            TestRun.started_at >= start,
            TestRun.started_at < end
        ).scalar() or 0
        
        # Sum API calls (if tracked)
        total_api_calls = db.query(func.sum(Trace.api_call_count)).filter(
            Trace.org_id == org_id,
            Trace.created_at >= start,
            Trace.created_at < end
        ).scalar() or 0
        
        report = {
            "org_id": org_id,
            "period": {
                "start": start_date,
                "end": end_date
            },
            "usage": {
                "traces_analyzed": trace_count,
                "test_runs": test_run_count,
                "total_api_calls": total_api_calls
            }
        }
        
        logger.info(f"Generated usage report for org {org_id}: {report}")
        return report
        
    finally:
        db.close()


# Fix import
from app.models.test import Test

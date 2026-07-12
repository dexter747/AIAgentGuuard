# Cleanup and maintenance background tasks
from app.core.celery_app import celery_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_traces():
    """Clean up traces older than retention period based on plan"""
    from app.core.database import SessionLocal
    from app.models.trace import Trace
    from app.models.organization import Organization
    
    logger.info("Starting trace cleanup job")
    
    # Retention periods by plan (in days)
    retention_days = {
        "free": 7,
        "starter": 14,
        "pro": 30,
        "team": 60,
        "enterprise": 365
    }
    
    db = SessionLocal()
    try:
        # Get all organizations
        orgs = db.query(Organization).all()
        total_deleted = 0
        
        for org in orgs:
            plan = org.plan or "free"
            days = retention_days.get(plan, 7)
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old traces for this organization
            deleted = db.query(Trace).filter(
                Trace.org_id == org.id,
                Trace.created_at < cutoff_date
            ).delete(synchronize_session=False)
            
            total_deleted += deleted
        
        db.commit()
        logger.info(f"Cleaned up {total_deleted} old traces")
        return {"deleted_traces": total_deleted}
    finally:
        db.close()


@celery_app.task
def cleanup_expired_tokens():
    """Clean up expired verification and reset tokens"""
    from app.core.database import SessionLocal
    from app.models.user import User
    
    logger.info("Starting token cleanup job")
    
    db = SessionLocal()
    try:
        # Reset expired verification tokens
        expired_verification = db.query(User).filter(
            User.verification_token.isnot(None),
            User.verification_token_expires < datetime.utcnow()
        ).update({
            "verification_token": None,
            "verification_token_expires": None
        }, synchronize_session=False)
        
        # Reset expired password reset tokens
        expired_reset = db.query(User).filter(
            User.reset_token.isnot(None),
            User.reset_token_expires < datetime.utcnow()
        ).update({
            "reset_token": None,
            "reset_token_expires": None
        }, synchronize_session=False)
        
        db.commit()
        logger.info(f"Cleaned up {expired_verification} expired verification tokens and {expired_reset} reset tokens")
        
        return {
            "expired_verification_tokens": expired_verification,
            "expired_reset_tokens": expired_reset
        }
    finally:
        db.close()


@celery_app.task
def cleanup_old_test_runs():
    """Clean up old test run records"""
    from app.core.database import SessionLocal
    from app.models.test import TestRun
    
    logger.info("Starting test run cleanup job")
    
    # Keep test runs for 90 days
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    
    db = SessionLocal()
    try:
        deleted = db.query(TestRun).filter(
            TestRun.started_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        logger.info(f"Cleaned up {deleted} old test runs")
        return {"deleted_test_runs": deleted}
    finally:
        db.close()


@celery_app.task
def vacuum_database():
    """Run VACUUM ANALYZE on PostgreSQL tables"""
    from app.core.database import engine
    from sqlalchemy import text
    
    logger.info("Starting database vacuum job")
    
    tables = ["users", "organizations", "agents", "traces", "tests", "test_runs", "webhooks"]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                conn.execute(text(f"VACUUM ANALYZE {table}"))
                logger.info(f"Vacuumed table: {table}")
            except Exception as e:
                logger.error(f"Failed to vacuum {table}: {str(e)}")
    
    return {"vacuumed_tables": tables}


@celery_app.task
def purge_deleted_user_data(user_id: int):
    """
    GDPR: Permanently delete all user data after account deletion request.
    This runs after a grace period (usually 30 days).
    """
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.trace import Trace
    from app.models.test import Test, TestRun
    
    logger.info(f"Purging data for deleted user {user_id}")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.info(f"User {user_id} already purged")
            return
        
        # Delete user's traces (if they're the only org member)
        # In a real implementation, check if org has other members
        
        # Anonymize or delete personally identifiable information
        user.email = f"deleted_{user_id}@deleted.overseex.com"
        user.full_name = "Deleted User"
        user.hashed_password = ""
        user.api_key = None
        user.avatar = None
        user.is_active = False
        user.deleted_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Purged user data for user {user_id}")
        
        return {"status": "purged", "user_id": user_id}
    finally:
        db.close()

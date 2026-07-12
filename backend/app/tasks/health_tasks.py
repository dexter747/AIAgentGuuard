# Health check background tasks
from app.core.celery_app import celery_app
from datetime import datetime
import httpx
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def run_all_health_checks():
    """Run health checks for all registered agents"""
    from app.core.database import SessionLocal
    from app.models.agent import Agent
    
    logger.info("Starting health check job")
    
    db = SessionLocal()
    try:
        # Get all agents with health check endpoints
        agents = db.query(Agent).filter(
            Agent.endpoint_url.isnot(None),
            Agent.endpoint_url != ""
        ).all()
        
        for agent in agents:
            run_single_health_check.delay(
                agent_id=agent.id,
                agent_name=agent.name,
                endpoint_url=agent.endpoint_url,
                org_id=agent.org_id
            )
        
        logger.info(f"Queued health checks for {len(agents)} agents")
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def run_single_health_check(self, agent_id: int, agent_name: str, endpoint_url: str, org_id: int):
    """Run health check for a single agent"""
    from app.core.database import SessionLocal
    from app.models.agent import Agent
    from app.tasks.email_tasks import send_health_alert_email
    
    start_time = datetime.utcnow()
    status = "healthy"
    error_message = None
    latency_ms = None
    
    try:
        # Make HTTP request to health endpoint
        with httpx.Client(timeout=30.0) as client:
            response = client.get(endpoint_url)
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code >= 500:
                status = "failing"
                error_message = f"Server error: {response.status_code}"
            elif response.status_code >= 400:
                status = "degraded"
                error_message = f"Client error: {response.status_code}"
            elif latency_ms > 5000:  # More than 5 seconds
                status = "degraded"
                error_message = f"High latency: {latency_ms}ms"
            else:
                status = "healthy"
                
    except httpx.TimeoutException:
        status = "failing"
        error_message = "Request timed out after 30 seconds"
        latency_ms = 30000
    except httpx.ConnectError:
        status = "failing"
        error_message = "Connection refused - endpoint unreachable"
    except Exception as e:
        status = "failing"
        error_message = str(e)
    
    # Update agent status in database
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            # Store health check result
            previous_status = getattr(agent, 'health_status', 'unknown')
            
            # If status changed to failing/degraded, send alert
            if status in ["failing", "degraded"] and previous_status == "healthy":
                # Get organization owner email
                from app.models.user import User
                owner = db.query(User).filter(User.org_id == org_id).first()
                if owner:
                    send_health_alert_email.delay(
                        email=owner.email,
                        agent_name=agent_name,
                        status=status,
                        error_message=error_message
                    )
            
            # Update agent health info
            agent.last_health_check = datetime.utcnow()
            agent.health_status = status
            db.commit()
            
        logger.info(f"Health check for {agent_name}: {status} ({latency_ms}ms)")
    finally:
        db.close()
    
    return {
        "agent_id": agent_id,
        "status": status,
        "latency_ms": latency_ms,
        "error": error_message
    }


@celery_app.task
def check_api_dependencies():
    """Check health of external API dependencies"""
    dependencies = {
        "openai": "https://api.openai.com/v1/models",
        "anthropic": "https://api.anthropic.com/v1/messages",
        "stripe": "https://api.stripe.com/v1",
    }
    
    results = {}
    
    for name, url in dependencies.items():
        try:
            with httpx.Client(timeout=10.0) as client:
                start = datetime.utcnow()
                response = client.get(url)
                latency = int((datetime.utcnow() - start).total_seconds() * 1000)
                results[name] = {
                    "status": "healthy" if response.status_code < 500 else "degraded",
                    "latency_ms": latency,
                    "status_code": response.status_code
                }
        except Exception as e:
            results[name] = {
                "status": "failing",
                "error": str(e)
            }
    
    logger.info(f"API dependency check results: {results}")
    return results

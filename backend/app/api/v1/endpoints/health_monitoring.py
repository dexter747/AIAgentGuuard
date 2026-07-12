"""
Health Check Monitoring API Endpoints
Configure and monitor agent health checks with alerting.
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.agent import Agent
from app.models.health_check import HealthCheck
from app.models.user import User
from app.services.health_monitor import HealthCheckMonitor, HealthStatus, health_monitor

router = APIRouter(prefix="/health-monitoring")


class HealthCheckConfigCreate(BaseModel):
    agent_id: str
    endpoint: str
    interval_seconds: int = 300  # 5 minutes
    timeout_seconds: int = 30
    alert_emails: Optional[List[str]] = None
    alert_slack_webhook: Optional[str] = None
    alert_pagerduty_key: Optional[str] = None


class HealthCheckConfigResponse(BaseModel):
    agent_id: str
    agent_name: str
    endpoint: str
    interval_seconds: int
    timeout_seconds: int
    alert_emails: List[str]
    enabled: bool


class HealthCheckResultResponse(BaseModel):
    agent_id: str
    status: str
    response_time_ms: int
    status_code: Optional[int]
    error_message: Optional[str]
    checked_at: str
    probe_region: str


class AgentHealthStatus(BaseModel):
    agent_id: str
    agent_name: str
    current_status: str
    consecutive_failures: int
    last_success: Optional[str]
    last_failure: Optional[str]
    uptime_percent: float
    uptime_percentage: float  # Alias for frontend compatibility
    avg_response_time_ms: float
    average_response_time: float  # Alias for frontend compatibility
    is_monitored: bool = False
    alert_email: Optional[str] = None
    last_check_time: Optional[str] = None


@router.post("/register")
async def register_health_check(
    config: HealthCheckConfigCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register an agent for health monitoring.
    
    Sets up periodic health checks at the specified interval.
    Alerts will be sent via configured channels (email, Slack, PagerDuty)
    when the agent fails health checks.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == config.agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get user email for alerts if not specified
    alert_emails = config.alert_emails or [current_user.email]
    
    # Register with health monitor
    health_monitor.register_agent(
        agent_id=str(agent.id),
        agent_name=agent.name,
        endpoint=config.endpoint,
        interval_seconds=config.interval_seconds,
        timeout_seconds=config.timeout_seconds,
        alert_emails=alert_emails,
        alert_slack_webhook=config.alert_slack_webhook,
        alert_pagerduty_key=config.alert_pagerduty_key
    )
    
    return {
        "message": f"Health monitoring registered for {agent.name}",
        "agent_id": str(agent.id),
        "endpoint": config.endpoint,
        "interval_seconds": config.interval_seconds,
        "alert_channels": {
            "email": alert_emails,
            "slack": bool(config.alert_slack_webhook),
            "pagerduty": bool(config.alert_pagerduty_key)
        }
    }


@router.delete("/unregister/{agent_id}")
async def unregister_health_check(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unregister an agent from health monitoring.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    health_monitor.unregister_agent(agent_id)
    
    return {
        "message": f"Health monitoring stopped for {agent.name}",
        "agent_id": agent_id
    }


@router.post("/check/{agent_id}")
async def trigger_health_check(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a health check for an agent.
    
    Runs an immediate health check and returns the result.
    Does not wait for the scheduled interval.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if registered
    if agent_id not in health_monitor.configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent not registered for health monitoring. Call /register first."
        )
    
    # Run health check
    try:
        result = await health_monitor.check_health(agent_id)
        
        # Save to database
        health_record = HealthCheck(
            agent_id=agent_id,
            probe_region=result.probe_region,
            status=result.status.value,
            response_time_ms=result.response_time_ms,
            response_body=result.response_body,
            error_message=result.error_message,
            checked_at=result.checked_at
        )
        db.add(health_record)
        db.commit()
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "status": result.status.value,
            "response_time_ms": result.response_time_ms,
            "status_code": result.status_code,
            "error_message": result.error_message,
            "checked_at": result.checked_at.isoformat(),
            "probe_region": result.probe_region
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/status/{agent_id}", response_model=AgentHealthStatus)
async def get_agent_health_status(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current health status for an agent.
    
    Returns the current status, recent history, uptime percentage,
    and average response time.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get status from monitor
    status_data = health_monitor.get_agent_status(agent_id)
    
    if not status_data:
        # If not in monitor, get from database
        recent_checks = db.query(HealthCheck).filter(
            HealthCheck.agent_id == agent_id
        ).order_by(HealthCheck.checked_at.desc()).limit(20).all()
        
        if not recent_checks:
            is_monitored = agent_id in health_monitor.configs
            alert_email = None
            if is_monitored:
                config = health_monitor.configs.get(agent_id)
                if config and config.alert_emails:
                    alert_email = config.alert_emails[0] if config.alert_emails else None
            
            return AgentHealthStatus(
                agent_id=agent_id,
                agent_name=agent.name,
                current_status="unknown",
                consecutive_failures=0,
                last_success=None,
                last_failure=None,
                uptime_percent=0.0,
                uptime_percentage=0.0,
                avg_response_time_ms=0.0,
                average_response_time=0.0,
                is_monitored=is_monitored,
                alert_email=alert_email,
                last_check_time=None
            )
        
        # Calculate from database
        healthy_count = len([c for c in recent_checks if c.status == "healthy"])
        uptime = (healthy_count / len(recent_checks)) * 100
        
        response_times = [c.response_time_ms for c in recent_checks if c.response_time_ms]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        last_success = next(
            (c.checked_at for c in recent_checks if c.status == "healthy"), 
            None
        )
        last_failure = next(
            (c.checked_at for c in recent_checks if c.status in ["unhealthy", "degraded"]),
            None
        )
        
        # Calculate consecutive failures
        consecutive_failures = 0
        for check in recent_checks:
            if check.status in ["unhealthy", "degraded"]:
                consecutive_failures += 1
            else:
                break
        
        # Check if monitored and get alert config
        is_monitored = agent_id in health_monitor.configs
        alert_email = None
        if is_monitored:
            config = health_monitor.configs.get(agent_id)
            if config and config.alert_emails:
                alert_email = config.alert_emails[0] if config.alert_emails else None
        
        return AgentHealthStatus(
            agent_id=agent_id,
            agent_name=agent.name,
            current_status=recent_checks[0].status if recent_checks else "unknown",
            consecutive_failures=consecutive_failures,
            last_success=last_success.isoformat() if last_success else None,
            last_failure=last_failure.isoformat() if last_failure else None,
            uptime_percent=round(uptime, 2),
            uptime_percentage=round(uptime, 2),
            avg_response_time_ms=round(avg_response, 2),
            average_response_time=round(avg_response, 2),
            is_monitored=is_monitored,
            alert_email=alert_email,
            last_check_time=recent_checks[0].checked_at.isoformat() if recent_checks else None
        )
    
    # Check if monitored and get alert config for status_data path
    is_monitored = agent_id in health_monitor.configs
    alert_email = None
    if is_monitored:
        config = health_monitor.configs.get(agent_id)
        if config and config.alert_emails:
            alert_email = config.alert_emails[0] if config.alert_emails else None
    
    return AgentHealthStatus(
        agent_id=status_data["agent_id"],
        agent_name=status_data["agent_name"],
        current_status=status_data["current_status"],
        consecutive_failures=status_data["consecutive_failures"],
        last_success=status_data["last_success"],
        last_failure=status_data["last_failure"],
        uptime_percent=status_data["uptime_percent"],
        uptime_percentage=status_data["uptime_percent"],
        avg_response_time_ms=status_data["avg_response_time_ms"],
        average_response_time=status_data["avg_response_time_ms"],
        is_monitored=is_monitored,
        alert_email=alert_email,
        last_check_time=status_data.get("last_check_time")
    )


@router.get("/history/{agent_id}")
async def get_health_history(
    agent_id: str,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health check history for an agent.
    
    Returns all health checks within the specified time period.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get history from database
    since = datetime.utcnow() - timedelta(hours=hours)
    
    checks = db.query(HealthCheck).filter(
        HealthCheck.agent_id == agent_id,
        HealthCheck.checked_at >= since
    ).order_by(HealthCheck.checked_at.desc()).all()
    
    # Calculate stats
    total_checks = len(checks)
    healthy_checks = len([c for c in checks if c.status == "healthy"])
    
    history_list = [
        {
            "id": str(c.id),
            "status": c.status,
            "response_time_ms": c.response_time_ms,
            "error_message": c.error_message,
            "checked_at": c.checked_at.isoformat() if c.checked_at else None,
            "probe_region": c.probe_region
        }
        for c in checks
    ]
    
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "period_hours": hours,
        "total_checks": total_checks,
        "healthy_checks": healthy_checks,
        "uptime_percent": round((healthy_checks / total_checks * 100) if total_checks else 0, 2),
        "history": history_list,
        "checks": history_list  # Alias for frontend compatibility
    }


@router.get("/all-statuses")
async def get_all_health_statuses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health status for all agents in the organization.
    """
    # Get all agents
    agents = db.query(Agent).filter(
        Agent.org_id == current_user.org_id
    ).all()
    
    statuses = []
    
    for agent in agents:
        # Get recent checks
        recent_checks = db.query(HealthCheck).filter(
            HealthCheck.agent_id == agent.id
        ).order_by(HealthCheck.checked_at.desc()).limit(10).all()
        
        if recent_checks:
            healthy_count = len([c for c in recent_checks if c.status == "healthy"])
            uptime = (healthy_count / len(recent_checks)) * 100
            current_status = recent_checks[0].status
        else:
            uptime = 0
            current_status = "no_data"
        
        # Check if registered for monitoring
        is_monitored = str(agent.id) in health_monitor.configs
        
        statuses.append({
            "agent_id": str(agent.id),
            "agent_name": agent.name,
            "current_status": current_status,
            "uptime_percent": round(uptime, 2),
            "is_monitored": is_monitored,
            "last_check": recent_checks[0].checked_at.isoformat() if recent_checks else None
        })
    
    return {
        "agents": statuses,
        "total_agents": len(agents),
        "monitored_agents": len([s for s in statuses if s["is_monitored"]]),
        "healthy_agents": len([s for s in statuses if s["current_status"] == "healthy"])
    }


@router.post("/update-alerts/{agent_id}")
async def update_alert_config(
    agent_id: str,
    alert_emails: Optional[List[str]] = None,
    alert_slack_webhook: Optional[str] = None,
    alert_pagerduty_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update alert configuration for an agent.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if agent_id not in health_monitor.configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent not registered for health monitoring"
        )
    
    # Update config
    config = health_monitor.configs[agent_id]
    
    if alert_emails is not None:
        config.alert_emails = alert_emails
    if alert_slack_webhook is not None:
        config.alert_slack_webhook = alert_slack_webhook
    if alert_pagerduty_key is not None:
        config.alert_pagerduty_key = alert_pagerduty_key
    
    return {
        "message": "Alert configuration updated",
        "agent_id": agent_id,
        "alert_emails": config.alert_emails,
        "slack_configured": bool(config.alert_slack_webhook),
        "pagerduty_configured": bool(config.alert_pagerduty_key)
    }


@router.get("/dashboard")
async def get_health_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive health monitoring dashboard data.
    
    Returns:
    - Overview statistics
    - All agent statuses
    - Recent alerts
    - Uptime trends
    """
    # Get all agents
    agents = db.query(Agent).filter(
        Agent.org_id == current_user.org_id
    ).all()
    
    # Define time window for 24 hours
    since_24h = datetime.utcnow() - timedelta(hours=24)
    
    agent_statuses = []
    total_uptime = 0
    total_response_time = 0
    agents_with_data = 0
    
    for agent in agents:
        # Get recent checks (last 24 hours)
        recent_checks = db.query(HealthCheck).filter(
            HealthCheck.agent_id == agent.id,
            HealthCheck.checked_at >= since_24h
        ).order_by(HealthCheck.checked_at.desc()).all()
        
        if recent_checks:
            healthy_count = len([c for c in recent_checks if c.status == "healthy"])
            uptime = (healthy_count / len(recent_checks)) * 100
            
            response_times = [c.response_time_ms for c in recent_checks if c.response_time_ms]
            avg_response = sum(response_times) / len(response_times) if response_times else 0
            
            current_status = recent_checks[0].status
            last_check = recent_checks[0].checked_at.isoformat()
            
            total_uptime += uptime
            total_response_time += avg_response
            agents_with_data += 1
        else:
            uptime = 0
            avg_response = 0
            current_status = "no_data"
            last_check = None
        
        # Check if monitored
        is_monitored = str(agent.id) in health_monitor.configs
        
        # Get consecutive failures
        consecutive_failures = 0
        for check in recent_checks:
            if check.status in ["unhealthy", "degraded"]:
                consecutive_failures += 1
            else:
                break
        
        agent_statuses.append({
            "agent_id": str(agent.id),
            "agent_name": agent.name,
            "current_status": current_status,
            "uptime_24h": round(uptime, 2),
            "avg_response_time_ms": round(avg_response, 2),
            "is_monitored": is_monitored,
            "last_check": last_check,
            "consecutive_failures": consecutive_failures,
            "total_checks_24h": len(recent_checks)
        })
    
    # Calculate overview stats
    healthy_agents = len([s for s in agent_statuses if s["current_status"] == "healthy"])
    degraded_agents = len([s for s in agent_statuses if s["current_status"] == "degraded"])
    unhealthy_agents = len([s for s in agent_statuses if s["current_status"] == "unhealthy"])
    
    avg_uptime = total_uptime / agents_with_data if agents_with_data else 0
    avg_response_time = total_response_time / agents_with_data if agents_with_data else 0
    
    # Get recent alerts (failures in last 24 hours)
    recent_alerts = db.query(HealthCheck).filter(
        HealthCheck.checked_at >= since_24h,
        HealthCheck.status.in_(["unhealthy", "degraded"])
    ).join(Agent).filter(
        Agent.org_id == current_user.org_id
    ).order_by(HealthCheck.checked_at.desc()).limit(10).all()
    
    return {
        "overview": {
            "total_agents": len(agents),
            "monitored_agents": len([s for s in agent_statuses if s["is_monitored"]]),
            "healthy_agents": healthy_agents,
            "degraded_agents": degraded_agents,
            "unhealthy_agents": unhealthy_agents,
            "avg_uptime_24h": round(avg_uptime, 2),
            "avg_response_time_ms": round(avg_response_time, 2)
        },
        "agents": agent_statuses,
        "recent_alerts": [
            {
                "id": str(alert.id),
                "agent_id": str(alert.agent_id),
                "agent_name": db.query(Agent).get(alert.agent_id).name,
                "status": alert.status,
                "error_message": alert.error_message,
                "checked_at": alert.checked_at.isoformat(),
                "response_time_ms": alert.response_time_ms
            }
            for alert in recent_alerts
        ]
    }

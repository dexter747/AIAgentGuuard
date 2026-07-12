"""
Health Monitor Scheduler - Automated health check probes
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import logging
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.health_check import HealthCheck
from app.models.agent import Agent
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class HealthProbe:
    """Individual health check probe"""
    
    def __init__(
        self,
        health_check_id: str,
        agent_id: str,
        endpoint: str,
        interval_minutes: int,
        timeout_seconds: int = 30
    ):
        self.health_check_id = health_check_id
        self.agent_id = agent_id
        self.endpoint = endpoint
        self.interval_minutes = interval_minutes
        self.timeout_seconds = timeout_seconds
        self.consecutive_failures = 0
        self.last_status = "unknown"
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute health check probe
        
        Returns:
            Dict with probe results
        """
        result = {
            "health_check_id": self.health_check_id,
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "unknown",
            "response_time_ms": None,
            "status_code": None,
            "error": None
        }
        
        try:
            start_time = datetime.utcnow()
            
            # Make HTTP request to health endpoint
            response = requests.get(
                self.endpoint,
                timeout=self.timeout_seconds,
                headers={"User-Agent": "AgentGuard-HealthProbe/1.0"}
            )
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result["response_time_ms"] = int(response_time)
            result["status_code"] = response.status_code
            
            # Determine health status
            if response.status_code == 200:
                result["status"] = "healthy"
                self.consecutive_failures = 0
            elif response.status_code in [500, 502, 503, 504]:
                result["status"] = "unhealthy"
                self.consecutive_failures += 1
            else:
                result["status"] = "degraded"
                self.consecutive_failures += 1
            
            logger.info(
                f"Health check {self.health_check_id}: {result['status']} "
                f"({result['status_code']}, {result['response_time_ms']}ms)"
            )
            
        except requests.exceptions.Timeout:
            result["status"] = "unhealthy"
            result["error"] = "Request timeout"
            self.consecutive_failures += 1
            logger.warning(f"Health check {self.health_check_id}: Timeout")
            
        except requests.exceptions.ConnectionError:
            result["status"] = "unhealthy"
            result["error"] = "Connection error"
            self.consecutive_failures += 1
            logger.warning(f"Health check {self.health_check_id}: Connection error")
            
        except Exception as e:
            result["status"] = "unhealthy"
            result["error"] = str(e)
            self.consecutive_failures += 1
            logger.error(f"Health check {self.health_check_id}: {str(e)}")
        
        # Update last status
        self.last_status = result["status"]
        
        return result


class HealthMonitorScheduler:
    """
    Scheduler for automated health check probes
    
    Features:
    - Configurable check intervals
    - Automatic alerting on failures
    - State tracking (healthy -> degraded -> unhealthy)
    - Email notifications
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.probes: Dict[str, HealthProbe] = {}
        self.running = False
    
    def start(self):
        """Start the health check scheduler"""
        if not self.running:
            self.scheduler.start()
            self.running = True
            logger.info("Health monitor scheduler started")
            
            # Load existing health checks from database
            self._load_health_checks()
    
    def stop(self):
        """Stop the health check scheduler"""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("Health monitor scheduler stopped")
    
    def add_health_check(
        self,
        health_check_id: str,
        agent_id: str,
        endpoint: str,
        interval_minutes: int,
        timeout_seconds: int = 30
    ):
        """
        Add a new health check to the scheduler
        
        Args:
            health_check_id: ID of the health check
            agent_id: ID of the agent being monitored
            endpoint: HTTP endpoint to check
            interval_minutes: How often to check (in minutes)
            timeout_seconds: Request timeout
        """
        # Create probe
        probe = HealthProbe(
            health_check_id=health_check_id,
            agent_id=agent_id,
            endpoint=endpoint,
            interval_minutes=interval_minutes,
            timeout_seconds=timeout_seconds
        )
        
        self.probes[health_check_id] = probe
        
        # Schedule the probe
        self.scheduler.add_job(
            func=self._execute_and_record_probe,
            args=[health_check_id],
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=health_check_id,
            name=f"Health check: {health_check_id}",
            replace_existing=True
        )
        
        logger.info(
            f"Added health check {health_check_id} "
            f"(interval: {interval_minutes}min, endpoint: {endpoint})"
        )
    
    def remove_health_check(self, health_check_id: str):
        """Remove a health check from the scheduler"""
        if health_check_id in self.probes:
            del self.probes[health_check_id]
        
        try:
            self.scheduler.remove_job(health_check_id)
            logger.info(f"Removed health check {health_check_id}")
        except Exception as e:
            logger.warning(f"Failed to remove job {health_check_id}: {e}")
    
    def _execute_and_record_probe(self, health_check_id: str):
        """Execute probe and record results in database"""
        if health_check_id not in self.probes:
            logger.warning(f"Probe {health_check_id} not found")
            return
        
        probe = self.probes[health_check_id]
        
        # Execute probe
        result = probe.execute()
        
        # Record in database
        try:
            db = SessionLocal()
            
            # Update health check record
            health_check = db.query(HealthCheck).filter(
                HealthCheck.id == health_check_id
            ).first()
            
            if health_check:
                health_check.last_check_at = datetime.utcnow()
                health_check.status = result["status"]
                health_check.last_response_time_ms = result["response_time_ms"]
                
                if result["status"] == "unhealthy":
                    health_check.failure_count = (health_check.failure_count or 0) + 1
                else:
                    health_check.failure_count = 0
                
                db.commit()
                
                # Check if we need to send alerts
                self._check_and_send_alerts(db, health_check, probe, result)
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to record probe result: {e}")
    
    def _check_and_send_alerts(
        self,
        db: Session,
        health_check: HealthCheck,
        probe: HealthProbe,
        result: Dict[str, Any]
    ):
        """Check if alerts should be sent"""
        # Alert on 3 consecutive failures
        if probe.consecutive_failures >= 3:
            # Get agent info
            agent = db.query(Agent).filter(Agent.id == probe.agent_id).first()
            
            if agent and health_check.alert_email:
                self._send_alert_email(
                    email=health_check.alert_email,
                    agent_name=agent.name,
                    endpoint=probe.endpoint,
                    consecutive_failures=probe.consecutive_failures,
                    last_error=result.get("error")
                )
        
        # Alert on recovery (was unhealthy, now healthy)
        if probe.last_status == "unhealthy" and result["status"] == "healthy":
            if health_check.alert_email:
                agent = db.query(Agent).filter(Agent.id == probe.agent_id).first()
                self._send_recovery_email(
                    email=health_check.alert_email,
                    agent_name=agent.name if agent else "Unknown",
                    endpoint=probe.endpoint
                )
    
    def _send_alert_email(
        self,
        email: str,
        agent_name: str,
        endpoint: str,
        consecutive_failures: int,
        last_error: Optional[str]
    ):
        """Send health check failure alert email"""
        try:
            subject = f"🚨 AgentGuard Health Check Alert: {agent_name}"
            
            body = f"""
            <h2>Health Check Failure Alert</h2>
            <p>The health check for <strong>{agent_name}</strong> is failing.</p>
            
            <h3>Details:</h3>
            <ul>
                <li><strong>Endpoint:</strong> {endpoint}</li>
                <li><strong>Consecutive Failures:</strong> {consecutive_failures}</li>
                <li><strong>Last Error:</strong> {last_error or 'None'}</li>
                <li><strong>Time:</strong> {datetime.utcnow().isoformat()}</li>
            </ul>
            
            <p>Please check your agent immediately.</p>
            
            <p>- AgentGuard</p>
            """
            
            email_service.send_email(
                to_email=email,
                subject=subject,
                body=body
            )
            
            logger.info(f"Sent alert email to {email} for {agent_name}")
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
    
    def _send_recovery_email(
        self,
        email: str,
        agent_name: str,
        endpoint: str
    ):
        """Send health check recovery email"""
        try:
            subject = f"✅ AgentGuard Health Check Recovered: {agent_name}"
            
            body = f"""
            <h2>Health Check Recovered</h2>
            <p>The health check for <strong>{agent_name}</strong> has recovered.</p>
            
            <h3>Details:</h3>
            <ul>
                <li><strong>Endpoint:</strong> {endpoint}</li>
                <li><strong>Status:</strong> Healthy</li>
                <li><strong>Time:</strong> {datetime.utcnow().isoformat()}</li>
            </ul>
            
            <p>Your agent is back online!</p>
            
            <p>- AgentGuard</p>
            """
            
            email_service.send_email(
                to_email=email,
                subject=subject,
                body=body
            )
            
            logger.info(f"Sent recovery email to {email} for {agent_name}")
            
        except Exception as e:
            logger.error(f"Failed to send recovery email: {e}")
    
    def _load_health_checks(self):
        """Load existing health checks from database and schedule them"""
        try:
            db = SessionLocal()
            
            # Get all active health checks
            health_checks = db.query(HealthCheck).filter(
                HealthCheck.is_active == True
            ).all()
            
            for hc in health_checks:
                self.add_health_check(
                    health_check_id=str(hc.id),
                    agent_id=str(hc.agent_id),
                    endpoint=hc.endpoint,
                    interval_minutes=hc.interval_minutes,
                    timeout_seconds=hc.timeout_seconds or 30
                )
            
            logger.info(f"Loaded {len(health_checks)} health checks from database")
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to load health checks: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.running,
            "total_probes": len(self.probes),
            "scheduled_jobs": len(self.scheduler.get_jobs()),
            "probes": [
                {
                    "health_check_id": probe.health_check_id,
                    "endpoint": probe.endpoint,
                    "interval_minutes": probe.interval_minutes,
                    "last_status": probe.last_status,
                    "consecutive_failures": probe.consecutive_failures
                }
                for probe in self.probes.values()
            ]
        }


# Global scheduler instance
health_scheduler = HealthMonitorScheduler()

"""
Health Check Monitoring Service for AgentGuard
Runs scheduled health probes and sends alerts when agents fail.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthCheckConfig:
    """Configuration for a health check."""
    agent_id: str
    agent_name: str
    endpoint: str
    interval_seconds: int = 300  # 5 minutes default
    timeout_seconds: int = 30
    expected_status_code: int = 200
    alert_emails: List[str] = field(default_factory=list)
    alert_slack_webhook: Optional[str] = None
    alert_pagerduty_key: Optional[str] = None
    consecutive_failures_threshold: int = 2  # Alert after 2 failures
    enabled: bool = True


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    agent_id: str
    status: HealthStatus
    response_time_ms: int
    status_code: Optional[int] = None
    response_body: Optional[Dict] = None
    error_message: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)
    probe_region: str = "us-east-1"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "status_code": self.status_code,
            "response_body": self.response_body,
            "error_message": self.error_message,
            "checked_at": self.checked_at.isoformat(),
            "probe_region": self.probe_region
        }


@dataclass
class AgentHealthState:
    """Tracks the health state of an agent over time."""
    agent_id: str
    consecutive_failures: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    current_status: HealthStatus = HealthStatus.UNKNOWN
    alert_sent: bool = False
    history: List[HealthCheckResult] = field(default_factory=list)


class HealthCheckMonitor:
    """
    Monitors agent health and sends alerts.
    
    Features:
    - Scheduled health checks at configurable intervals
    - Multi-region probing (simulated)
    - Intelligent alerting with escalation
    - Integration with email, Slack, PagerDuty
    """
    
    def __init__(self, db_session=None):
        self.configs: Dict[str, HealthCheckConfig] = {}
        self.states: Dict[str, AgentHealthState] = {}
        self.running = False
        self.tasks: Dict[str, asyncio.Task] = {}
        self.db_session = db_session
        
        # Alert thresholds
        self.THRESHOLDS = {
            1: AlertSeverity.INFO,      # 1 failure - log only
            2: AlertSeverity.WARNING,   # 2 failures - email
            3: AlertSeverity.CRITICAL,  # 3+ failures - email + slack + pagerduty
        }
        
        # Simulated probe regions
        self.PROBE_REGIONS = ["us-east-1", "eu-west-1", "ap-south-1"]
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        endpoint: str,
        interval_seconds: int = 300,
        timeout_seconds: int = 30,
        alert_emails: List[str] = None,
        alert_slack_webhook: str = None,
        alert_pagerduty_key: str = None
    ):
        """Register an agent for health monitoring."""
        config = HealthCheckConfig(
            agent_id=agent_id,
            agent_name=agent_name,
            endpoint=endpoint,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            alert_emails=alert_emails or [],
            alert_slack_webhook=alert_slack_webhook,
            alert_pagerduty_key=alert_pagerduty_key
        )
        
        self.configs[agent_id] = config
        self.states[agent_id] = AgentHealthState(agent_id=agent_id)
        
        logger.info(f"Registered health check for agent {agent_name} ({agent_id})")
        return config
    
    def unregister_agent(self, agent_id: str):
        """Remove an agent from health monitoring."""
        if agent_id in self.configs:
            del self.configs[agent_id]
        if agent_id in self.states:
            del self.states[agent_id]
        if agent_id in self.tasks:
            self.tasks[agent_id].cancel()
            del self.tasks[agent_id]
    
    async def check_health(self, agent_id: str) -> HealthCheckResult:
        """
        Perform a single health check for an agent.
        """
        if agent_id not in self.configs:
            raise ValueError(f"Agent {agent_id} not registered for health checks")
        
        config = self.configs[agent_id]
        start_time = datetime.utcnow()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.endpoint,
                    json={
                        "type": "health_check",
                        "timestamp": start_time.isoformat(),
                        "probe_id": f"{self.PROBE_REGIONS[0]}-probe"
                    },
                    timeout=aiohttp.ClientTimeout(total=config.timeout_seconds),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    end_time = datetime.utcnow()
                    response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                    
                    try:
                        response_body = await response.json()
                    except:
                        response_body = {"raw": await response.text()}
                    
                    # Determine health status
                    if response.status == config.expected_status_code:
                        status = HealthStatus.HEALTHY
                        # Check for degraded status in response
                        if response_body.get("status") == "degraded":
                            status = HealthStatus.DEGRADED
                    elif response.status >= 500:
                        status = HealthStatus.UNHEALTHY
                    else:
                        status = HealthStatus.DEGRADED
                    
                    result = HealthCheckResult(
                        agent_id=agent_id,
                        status=status,
                        response_time_ms=response_time_ms,
                        status_code=response.status,
                        response_body=response_body,
                        probe_region=self.PROBE_REGIONS[0]
                    )
                    
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                agent_id=agent_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=config.timeout_seconds * 1000,
                error_message=f"Timeout after {config.timeout_seconds}s"
            )
            
        except aiohttp.ClientError as e:
            result = HealthCheckResult(
                agent_id=agent_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message=f"Connection error: {str(e)}"
            )
            
        except Exception as e:
            result = HealthCheckResult(
                agent_id=agent_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message=f"Unexpected error: {str(e)}"
            )
        
        # Update state and process result
        await self._process_result(result)
        
        return result
    
    async def _process_result(self, result: HealthCheckResult):
        """Process a health check result and trigger alerts if needed."""
        agent_id = result.agent_id
        state = self.states.get(agent_id)
        config = self.configs.get(agent_id)
        
        if not state or not config:
            return
        
        # Update history
        state.history.append(result)
        if len(state.history) > 100:  # Keep last 100 results
            state.history = state.history[-100:]
        
        # Update state based on result
        if result.status == HealthStatus.HEALTHY:
            # Recovery
            if state.consecutive_failures > 0:
                await self._send_recovery_alert(config, state, result)
            
            state.consecutive_failures = 0
            state.last_success = result.checked_at
            state.current_status = HealthStatus.HEALTHY
            state.alert_sent = False
            
        else:
            # Failure
            state.consecutive_failures += 1
            state.last_failure = result.checked_at
            state.current_status = result.status
            
            # Check if we should alert
            await self._check_and_alert(config, state, result)
        
        # Save to database if available
        if self.db_session:
            await self._save_to_database(result)
    
    async def _check_and_alert(
        self,
        config: HealthCheckConfig,
        state: AgentHealthState,
        result: HealthCheckResult
    ):
        """Check thresholds and send appropriate alerts."""
        failures = state.consecutive_failures
        
        # Determine severity based on failures
        severity = AlertSeverity.INFO
        for threshold, sev in self.THRESHOLDS.items():
            if failures >= threshold:
                severity = sev
        
        # Only alert for WARNING and CRITICAL
        if severity == AlertSeverity.INFO:
            logger.info(f"Agent {config.agent_name} health check failed (attempt {failures})")
            return
        
        # Don't spam alerts - only send on threshold crossings
        thresholds_crossed = [t for t in self.THRESHOLDS.keys() if failures == t]
        
        if not thresholds_crossed and state.alert_sent:
            return
        
        # Send alerts based on severity
        if severity == AlertSeverity.WARNING:
            await self._send_email_alert(config, state, result)
            state.alert_sent = True
            
        elif severity == AlertSeverity.CRITICAL:
            await self._send_email_alert(config, state, result)
            await self._send_slack_alert(config, state, result)
            await self._send_pagerduty_alert(config, state, result)
            state.alert_sent = True
    
    async def _send_email_alert(
        self,
        config: HealthCheckConfig,
        state: AgentHealthState,
        result: HealthCheckResult
    ):
        """Send email alert for health check failure."""
        if not config.alert_emails:
            logger.warning(f"No email addresses configured for agent {config.agent_name}")
            return
        
        # Import email service
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            for email in config.alert_emails:
                await email_service.send_health_alert_email(
                    to_email=email,
                    agent_name=config.agent_name,
                    status=result.status.value,
                    consecutive_failures=state.consecutive_failures,
                    error_message=result.error_message,
                    endpoint=config.endpoint,
                    last_success=state.last_success.isoformat() if state.last_success else "Never"
                )
                
            logger.info(f"Sent email alerts to {len(config.alert_emails)} recipients")
            
        except ImportError:
            logger.warning("Email service not available, skipping email alert")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    async def _send_slack_alert(
        self,
        config: HealthCheckConfig,
        state: AgentHealthState,
        result: HealthCheckResult
    ):
        """Send Slack alert for health check failure."""
        if not config.alert_slack_webhook:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"🚨 Agent Health Check Failed: {config.agent_name}",
                                "emoji": True
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": f"*Status:*\n{result.status.value.upper()}"},
                                {"type": "mrkdwn", "text": f"*Failures:*\n{state.consecutive_failures} consecutive"},
                                {"type": "mrkdwn", "text": f"*Endpoint:*\n{config.endpoint}"},
                                {"type": "mrkdwn", "text": f"*Time:*\n{result.checked_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"}
                            ]
                        }
                    ]
                }
                
                if result.error_message:
                    payload["blocks"].append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Error:*\n```{result.error_message}```"
                        }
                    })
                
                async with session.post(
                    config.alert_slack_webhook,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.info("Sent Slack alert successfully")
                    else:
                        logger.error(f"Failed to send Slack alert: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    async def _send_pagerduty_alert(
        self,
        config: HealthCheckConfig,
        state: AgentHealthState,
        result: HealthCheckResult
    ):
        """Send PagerDuty alert for critical health check failures."""
        if not config.alert_pagerduty_key:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "routing_key": config.alert_pagerduty_key,
                    "event_action": "trigger",
                    "dedup_key": f"agentguard-{config.agent_id}",
                    "payload": {
                        "summary": f"Agent {config.agent_name} health check failed ({state.consecutive_failures} consecutive failures)",
                        "severity": "critical",
                        "source": "agentguard",
                        "component": config.agent_name,
                        "group": "ai-agents",
                        "custom_details": {
                            "agent_id": config.agent_id,
                            "endpoint": config.endpoint,
                            "error": result.error_message,
                            "status": result.status.value,
                            "consecutive_failures": state.consecutive_failures
                        }
                    }
                }
                
                async with session.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 202:
                        logger.info("Sent PagerDuty alert successfully")
                    else:
                        logger.error(f"Failed to send PagerDuty alert: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")
    
    async def _send_recovery_alert(
        self,
        config: HealthCheckConfig,
        state: AgentHealthState,
        result: HealthCheckResult
    ):
        """Send recovery notification when agent becomes healthy again."""
        if not state.alert_sent:
            return
        
        logger.info(f"Agent {config.agent_name} recovered after {state.consecutive_failures} failures")
        
        # Send recovery email
        if config.alert_emails:
            try:
                from app.services.email_service import EmailService
                email_service = EmailService()
                
                for email in config.alert_emails:
                    await email_service.send_health_recovery_email(
                        to_email=email,
                        agent_name=config.agent_name,
                        downtime_duration=self._calculate_downtime(state)
                    )
            except Exception as e:
                logger.error(f"Failed to send recovery email: {e}")
        
        # Send Slack recovery
        if config.alert_slack_webhook:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "blocks": [
                            {
                                "type": "header",
                                "text": {
                                    "type": "plain_text",
                                    "text": f"✅ Agent Recovered: {config.agent_name}",
                                    "emoji": True
                                }
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"Agent is healthy again. Downtime: {self._calculate_downtime(state)}"
                                }
                            }
                        ]
                    }
                    await session.post(config.alert_slack_webhook, json=payload)
            except:
                pass
        
        # Resolve PagerDuty
        if config.alert_pagerduty_key:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "routing_key": config.alert_pagerduty_key,
                        "event_action": "resolve",
                        "dedup_key": f"agentguard-{config.agent_id}"
                    }
                    await session.post(
                        "https://events.pagerduty.com/v2/enqueue",
                        json=payload
                    )
            except:
                pass
    
    def _calculate_downtime(self, state: AgentHealthState) -> str:
        """Calculate downtime duration."""
        if not state.last_failure or not state.last_success:
            return "Unknown"
        
        if state.last_success > state.last_failure:
            duration = state.last_success - state.last_failure
        else:
            duration = datetime.utcnow() - state.last_failure
        
        minutes = int(duration.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes} minutes"
        hours = minutes / 60
        return f"{hours:.1f} hours"
    
    async def _save_to_database(self, result: HealthCheckResult):
        """Save health check result to database."""
        try:
            from app.models.health_check import HealthCheck
            
            health_check = HealthCheck(
                agent_id=result.agent_id,
                probe_region=result.probe_region,
                status=result.status.value,
                response_time_ms=result.response_time_ms,
                response_body=result.response_body,
                error_message=result.error_message,
                checked_at=result.checked_at
            )
            
            self.db_session.add(health_check)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to save health check to database: {e}")
    
    async def start_monitoring(self, agent_id: str):
        """Start monitoring loop for a specific agent."""
        if agent_id not in self.configs:
            raise ValueError(f"Agent {agent_id} not registered")
        
        config = self.configs[agent_id]
        
        async def monitor_loop():
            while self.running:
                try:
                    await self.check_health(agent_id)
                except Exception as e:
                    logger.error(f"Health check error for {agent_id}: {e}")
                
                await asyncio.sleep(config.interval_seconds)
        
        self.tasks[agent_id] = asyncio.create_task(monitor_loop())
        logger.info(f"Started monitoring for agent {agent_id}")
    
    async def start_all(self):
        """Start monitoring all registered agents."""
        self.running = True
        for agent_id in self.configs:
            await self.start_monitoring(agent_id)
        logger.info(f"Started monitoring {len(self.configs)} agents")
    
    async def stop_all(self):
        """Stop all monitoring tasks."""
        self.running = False
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()
        logger.info("Stopped all health monitoring")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current status for an agent."""
        state = self.states.get(agent_id)
        config = self.configs.get(agent_id)
        
        if not state or not config:
            return None
        
        # Calculate uptime
        recent_checks = [r for r in state.history[-20:] if r.status == HealthStatus.HEALTHY]
        uptime_percent = (len(recent_checks) / max(len(state.history[-20:]), 1)) * 100
        
        # Calculate average response time
        recent_times = [r.response_time_ms for r in state.history[-20:] if r.response_time_ms]
        avg_response_time = sum(recent_times) / len(recent_times) if recent_times else 0
        
        return {
            "agent_id": agent_id,
            "agent_name": config.agent_name,
            "current_status": state.current_status.value,
            "consecutive_failures": state.consecutive_failures,
            "last_success": state.last_success.isoformat() if state.last_success else None,
            "last_failure": state.last_failure.isoformat() if state.last_failure else None,
            "uptime_percent": round(uptime_percent, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "recent_history": [r.to_dict() for r in state.history[-10:]]
        }
    
    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Get status for all monitored agents."""
        return [
            status for status in 
            [self.get_agent_status(aid) for aid in self.configs]
            if status
        ]


# Singleton instance
health_monitor = HealthCheckMonitor()

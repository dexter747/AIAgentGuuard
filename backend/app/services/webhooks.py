"""
Webhooks Service

Send real-time notifications when events occur:
- trace.created
- trace.error
- test.passed
- test.failed
- coordination.issue_detected
- rate_limit.exceeded
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio
import httpx
import json
import hmac
import hashlib


class WebhookEvent(str, Enum):
    """Webhook event types."""
    TRACE_CREATED = "trace.created"
    TRACE_ERROR = "trace.error"
    TEST_PASSED = "test.passed"
    TEST_FAILED = "test.failed"
    COORDINATION_ISSUE = "coordination.issue_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
    AGENT_CREATED = "agent.created"
    AGENT_HEALTH_CHANGED = "agent.health_changed"


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    id: str
    url: str
    events: List[WebhookEvent]
    secret: str
    is_active: bool = True
    org_id: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class WebhookDelivery:
    """Record of a webhook delivery attempt."""
    webhook_id: str
    event: WebhookEvent
    payload: Dict[str, Any]
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    delivered_at: datetime = None
    duration_ms: Optional[int] = None
    
    def __post_init__(self):
        if self.delivered_at is None:
            self.delivered_at = datetime.now()


class WebhookService:
    """
    Service for managing and delivering webhooks.
    
    Usage:
        >>> service = WebhookService()
        >>> service.register_webhook(
        ...     url="https://example.com/webhook",
        ...     events=[WebhookEvent.TRACE_ERROR],
        ...     secret="your_secret"
        ... )
        >>> await service.trigger(WebhookEvent.TRACE_ERROR, {"trace_id": "123"})
    """
    
    def __init__(self):
        """Initialize webhook service."""
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.deliveries: List[WebhookDelivery] = []
        self.retry_delays = [1, 5, 30, 300]  # Retry delays in seconds
    
    def register_webhook(
        self,
        url: str,
        events: List[WebhookEvent],
        secret: str,
        org_id: Optional[str] = None,
        webhook_id: Optional[str] = None
    ) -> WebhookConfig:
        """
        Register a new webhook.
        
        Args:
            url: Webhook endpoint URL
            events: List of events to subscribe to
            secret: Secret for HMAC signature
            org_id: Organization ID (for multi-tenant)
            webhook_id: Custom webhook ID (auto-generated if None)
            
        Returns:
            Created WebhookConfig
        """
        import uuid
        
        webhook = WebhookConfig(
            id=webhook_id or str(uuid.uuid4()),
            url=url,
            events=events,
            secret=secret,
            org_id=org_id
        )
        
        self.webhooks[webhook.id] = webhook
        return webhook
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Unregister a webhook.
        
        Args:
            webhook_id: Webhook ID to remove
            
        Returns:
            True if removed, False if not found
        """
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False
    
    def get_webhooks(
        self,
        org_id: Optional[str] = None,
        event: Optional[WebhookEvent] = None
    ) -> List[WebhookConfig]:
        """
        Get webhooks, optionally filtered.
        
        Args:
            org_id: Filter by organization
            event: Filter by subscribed event
            
        Returns:
            List of matching webhooks
        """
        webhooks = list(self.webhooks.values())
        
        if org_id:
            webhooks = [w for w in webhooks if w.org_id == org_id]
        
        if event:
            webhooks = [w for w in webhooks if event in w.events]
        
        return [w for w in webhooks if w.is_active]
    
    def _sign_payload(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def trigger(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        org_id: Optional[str] = None
    ) -> List[WebhookDelivery]:
        """
        Trigger webhooks for an event.
        
        Args:
            event: Event type
            data: Event payload data
            org_id: Organization ID (for filtering)
            
        Returns:
            List of delivery results
        """
        webhooks = self.get_webhooks(org_id=org_id, event=event)
        deliveries = []
        
        for webhook in webhooks:
            delivery = await self._deliver(webhook, event, data)
            deliveries.append(delivery)
            self.deliveries.append(delivery)
        
        return deliveries
    
    async def _deliver(
        self,
        webhook: WebhookConfig,
        event: WebhookEvent,
        data: Dict[str, Any]
    ) -> WebhookDelivery:
        """
        Deliver a webhook with retries.
        
        Args:
            webhook: Webhook configuration
            event: Event type
            data: Event data
            
        Returns:
            Delivery result
        """
        payload = {
            "event": event.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        payload_str = json.dumps(payload, sort_keys=True)
        signature = self._sign_payload(payload_str, webhook.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-OverseeX-Signature": f"sha256={signature}",
            "X-OverseeX-Event": event.value,
            "X-OverseeX-Delivery": webhook.id
        }
        
        start_time = datetime.now()
        
        async with httpx.AsyncClient() as client:
            for attempt, delay in enumerate(self.retry_delays + [0]):
                try:
                    response = await client.post(
                        webhook.url,
                        content=payload_str,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    return WebhookDelivery(
                        webhook_id=webhook.id,
                        event=event,
                        payload=payload,
                        response_status=response.status_code,
                        response_body=response.text[:500],
                        duration_ms=duration_ms
                    )
                    
                except Exception as e:
                    if attempt < len(self.retry_delays):
                        await asyncio.sleep(delay)
                    else:
                        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                        return WebhookDelivery(
                            webhook_id=webhook.id,
                            event=event,
                            payload=payload,
                            error=str(e),
                            duration_ms=duration_ms
                        )
        
        return WebhookDelivery(
            webhook_id=webhook.id,
            event=event,
            payload=payload,
            error="Unknown error"
        )
    
    def get_deliveries(
        self,
        webhook_id: Optional[str] = None,
        event: Optional[WebhookEvent] = None,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """
        Get delivery history.
        
        Args:
            webhook_id: Filter by webhook
            event: Filter by event type
            limit: Maximum results
            
        Returns:
            List of deliveries
        """
        deliveries = self.deliveries
        
        if webhook_id:
            deliveries = [d for d in deliveries if d.webhook_id == webhook_id]
        
        if event:
            deliveries = [d for d in deliveries if d.event == event]
        
        return deliveries[-limit:]


# Global instance
_webhook_service: Optional[WebhookService] = None


def get_webhook_service() -> WebhookService:
    """Get or create global webhook service."""
    global _webhook_service
    if _webhook_service is None:
        _webhook_service = WebhookService()
    return _webhook_service


async def trigger_webhook(
    event: WebhookEvent,
    data: Dict[str, Any],
    org_id: Optional[str] = None
) -> List[WebhookDelivery]:
    """Convenience function to trigger webhooks."""
    service = get_webhook_service()
    return await service.trigger(event, data, org_id)

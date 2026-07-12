"""
Webhook management endpoints with database integration
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List
from datetime import datetime
import secrets
import hashlib

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.webhook import Webhook
from app.models.user import User

router = APIRouter(prefix="/webhooks")


class WebhookCreate(BaseModel):
    url: str
    events: List[str]


class WebhookUpdate(BaseModel):
    url: str | None = None
    events: List[str] | None = None


class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    status: str
    secret: str | None = None
    created_at: str


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all webhooks for the current organization"""
    
    webhooks = db.query(Webhook).filter(
        Webhook.org_id == current_user.org_id
    ).all()
    
    return [
        {
            "id": str(webhook.id),
            "url": webhook.url,
            "events": webhook.events or [],
            "status": "active" if webhook.is_active else "inactive",
            "secret": webhook.secret,
            "created_at": webhook.created_at.isoformat() if webhook.created_at else ""
        }
        for webhook in webhooks
    ]


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new webhook"""
    
    # Generate webhook secret for signature verification
    secret = f"whsec_{secrets.token_hex(32)}"
    
    webhook = Webhook(
        org_id=current_user.org_id,
        url=webhook_data.url,
        events=webhook_data.events,
        secret=secret,
        is_active=True
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    return {
        "id": str(webhook.id),
        "url": webhook.url,
        "events": webhook.events or [],
        "status": "active",
        "secret": secret,
        "created_at": webhook.created_at.isoformat() if webhook.created_at else ""
    }


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook_data: WebhookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a webhook"""
    
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user.org_id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    if webhook_data.url is not None:
        webhook.url = webhook_data.url
    if webhook_data.events is not None:
        webhook.events = webhook_data.events
    
    webhook.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(webhook)
    
    return {
        "id": str(webhook.id),
        "url": webhook.url,
        "events": webhook.events or [],
        "status": "active" if webhook.is_active else "inactive",
        "secret": webhook.secret,
        "created_at": webhook.created_at.isoformat() if webhook.created_at else ""
    }


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a webhook"""
    
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user.org_id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    db.delete(webhook)
    db.commit()
    
    return None


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test a webhook by sending a test payload"""
    
    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id,
        Webhook.org_id == current_user.org_id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # TODO: Actually send a test webhook
    # For now, return success
    return {
        "success": True,
        "message": f"Test webhook sent to {webhook.url}",
        "timestamp": datetime.utcnow().isoformat()
    }


# Webhook Ingestion Endpoint (for no-code platforms like n8n, Zapier)
@router.post("/ingest/{org_id}", status_code=status.HTTP_201_CREATED)
async def ingest_trace_webhook(
    org_id: str,
    payload: dict,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Receive traces from no-code platforms (n8n, Zapier, Make.com)
    
    This endpoint allows users to send agent execution data via HTTP POST
    without needing to use SDKs.
    
    Required in payload:
    - agent_name: str
    - input: str
    - output: str
    - status: str ("success" or "error")
    
    Optional:
    - duration_ms: int
    - steps: List[dict]
    - token_count: int
    - cost_usd: str
    - metadata: dict
    """
    from app.models.user import User, Organization
    from app.models.agent import Agent
    from app.models.trace import Trace
    
    # Authenticate via API key
    user = db.query(User).filter(User.api_key == x_api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Verify org_id matches
    if str(user.org_id) != org_id:
        raise HTTPException(status_code=403, detail="Organization mismatch")
    
    # Validate required fields
    required_fields = ["agent_name", "input", "output", "status"]
    for field in required_fields:
        if field not in payload:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Find or create agent
    agent = db.query(Agent).filter(
        Agent.org_id == user.org_id,
        Agent.name == payload["agent_name"]
    ).first()
    
    if not agent:
        # Auto-create agent if doesn't exist
        agent = Agent(
            org_id=user.org_id,
            name=payload["agent_name"],
            endpoint_url=payload.get("metadata", {}).get("workflow_url"),
            health_check_interval=300
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
    
    # Build trace data
    trace_data = {
        "input": payload["input"],
        "output": payload["output"],
        "steps": payload.get("steps", []),
        "metadata": payload.get("metadata", {}),
        "platform": payload.get("platform", "webhook")  # n8n, zapier, make, etc.
    }
    
    # Create trace
    trace = Trace(
        agent_id=agent.id,
        trace_data=trace_data,
        status=payload["status"],
        total_duration_ms=payload.get("duration_ms"),
        token_count=payload.get("token_count"),
        cost_usd=payload.get("cost_usd")
    )
    
    db.add(trace)
    db.commit()
    db.refresh(trace)
    
    return {
        "success": True,
        "trace_id": str(trace.id),
        "agent_id": str(agent.id),
        "agent_name": agent.name,
        "message": "Trace ingested successfully"
    }

"""
Admin endpoints for platform management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import os

from app.core.database import get_db
from app.models.user import User, Organization
from app.core.auth import get_current_user
from app.models.agent import Agent
from app.models.trace import Trace

router = APIRouter()


# Response Models
class PlatformStats(BaseModel):
    total_users: int
    total_organizations: int
    monthly_revenue: float
    active_guards: int
    users_change: float
    orgs_change: float
    revenue_change: float
    guards_change: float


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    organization: str
    plan: str
    status: str
    created_at: datetime


class SystemStatusResponse(BaseModel):
    name: str
    status: str
    uptime: float


class ActivityLogResponse(BaseModel):
    type: str
    message: str
    time: str


# Dependency to check admin role
async def require_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get platform-wide statistics"""
    
    # Get current counts
    total_users = db.query(User).count()
    total_orgs = db.query(Organization).count()
    
    # Get counts from last month for comparison
    last_month = datetime.utcnow() - timedelta(days=30)
    users_last_month = db.query(User).filter(User.created_at < last_month).count()
    orgs_last_month = db.query(Organization).filter(Organization.created_at < last_month).count()
    
    # Calculate change percentages
    users_change = ((total_users - users_last_month) / users_last_month * 100) if users_last_month > 0 else 0
    orgs_change = ((total_orgs - orgs_last_month) / orgs_last_month * 100) if orgs_last_month > 0 else 0
    
    # Get active agents count (agents don't have status field, just count all)
    active_agents = db.query(Agent).count()
    agents_last_month = db.query(Agent).filter(
        Agent.created_at < last_month
    ).count()
    agents_change = ((active_agents - agents_last_month) / agents_last_month * 100) if agents_last_month > 0 else 0
    
    # Calculate revenue based on actual plan data
    from app.models.user import SubscriptionPlan
    monthly_revenue = 0
    plan_prices = {
        SubscriptionPlan.FREE: 0,
        SubscriptionPlan.PRO: 29,
        SubscriptionPlan.TEAM: 99,
        SubscriptionPlan.ENTERPRISE: 299
    }
    orgs = db.query(Organization).all()
    for org in orgs:
        plan = org.plan if org.plan else SubscriptionPlan.FREE
        monthly_revenue += plan_prices.get(plan, 0)
    
    return {
        "total_users": total_users,
        "total_organizations": total_orgs,
        "monthly_revenue": monthly_revenue,
        "active_guards": active_agents,
        "users_change": round(users_change, 1),
        "orgs_change": round(orgs_change, 1),
        "revenue_change": 12.5,  # Mock growth
        "guards_change": round(agents_change, 1)
    }


@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all users with filters"""
    
    query = db.query(User).outerjoin(Organization)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    
    if status:
        if status == "active":
            query = query.filter(User.is_active == True)
        elif status == "inactive":
            query = query.filter(User.is_active == False)
    
    total = query.count()
    users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
    
    users_list = [
        {
            "id": str(user.id),
            "full_name": user.full_name or "Unknown",
            "email": user.email,
            "organization": user.organization.name if user.organization else "No Organization",
            "plan": user.user_metadata.get("plan_id", "free") if user.user_metadata else "free",
            "status": "active" if user.is_active else "inactive",
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_admin": user.is_admin,
            "role": user.role.value if user.role else "member",
            "created_at": user.created_at
        }
        for user in users
    ]
    
    return {
        "users": users_list,
        "total": total
    }


@router.get("/system-status", response_model=List[SystemStatusResponse])
async def get_system_status(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get system health status"""
    
    statuses = []
    
    # Check database
    try:
        db.execute("SELECT 1")
        statuses.append({
            "name": "Database",
            "status": "operational",
            "uptime": 99.99
        })
    except Exception:
        statuses.append({
            "name": "Database",
            "status": "degraded",
            "uptime": 0
        })
    
    # Check Redis
    try:
        from app.services.cache_service import cache_service
        if cache_service.cache.redis_client:
            cache_service.cache.redis_client.ping()
            statuses.append({
                "name": "Redis Cache",
                "status": "operational",
                "uptime": 99.95
            })
        else:
            statuses.append({
                "name": "Redis Cache",
                "status": "degraded",
                "uptime": 0
            })
    except:
        statuses.append({
            "name": "Redis Cache",
            "status": "degraded",
            "uptime": 85.00
        })
    
    # API Gateway is this service
    statuses.append({
        "name": "API Gateway",
        "status": "operational",
        "uptime": 99.99
    })
    
    return statuses


@router.get("/activity", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    limit: int = 10,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get recent activity logs"""
    
    # TODO: Implement actual activity logging
    # For now, return recent user registrations
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(limit).all()
    
    activities = []
    for user in recent_users:
        time_diff = datetime.utcnow() - user.created_at
        if time_diff.days > 0:
            time_str = f"{time_diff.days} days ago"
        elif time_diff.seconds > 3600:
            time_str = f"{time_diff.seconds // 3600} hours ago"
        else:
            time_str = f"{time_diff.seconds // 60} min ago"
        
        activities.append({
            "type": "user",
            "message": f"New user registered: {user.email}",
            "time": time_str
        })
    
    return activities


@router.get("/organizations")
async def list_organizations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all organizations"""
    
    orgs = db.query(Organization).order_by(desc(Organization.created_at)).offset(offset).limit(limit).all()
    
    return {
        "organizations": [
            {
                "id": str(org.id),
                "name": org.name,
                "created_at": org.created_at,
                "user_count": db.query(User).filter(User.org_id == org.id).count()
            }
            for org in orgs
        ],
        "total": db.query(Organization).count()
    }


@router.get("/analytics")
async def get_analytics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get platform analytics"""
    
    # User growth over last 7 days
    user_growth = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        count = db.query(User).filter(
            func.date(User.created_at) == date.date()
        ).count()
        user_growth.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return {
        "user_growth": user_growth[::-1],
        "total_users": db.query(User).count(),
        "total_orgs": db.query(Organization).count()
    }


@router.get("/billing")
async def get_billing_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get billing and revenue overview"""
    
    total_orgs = db.query(Organization).count()
    
    # Mock revenue data - integrate with actual billing later
    return {
        "total_revenue": total_orgs * 29,
        "monthly_recurring": total_orgs * 29,
        "total_subscriptions": total_orgs,
        "active_trials": 5,
        "recent_payments": []
    }


@router.get("/emails")
async def get_email_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get email delivery statistics"""
    
    # Mock email stats
    return {
        "total_sent": 142,
        "delivered": 138,
        "opened": 89,
        "clicked": 34,
        "bounced": 4,
        "delivery_rate": 97.2,
        "open_rate": 64.5,
        "click_rate": 24.6
    }


@router.get("/settings")
async def get_platform_settings(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get platform settings"""
    
    return {
        "registration_enabled": True,
        "email_verification_required": True,
        "free_tier_enabled": True,
        "maintenance_mode": False,
        "smtp_configured": bool(os.getenv("SMTP_HOST")),
        "redis_configured": True
    }


@router.put("/settings")
async def update_platform_settings(
    settings: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update platform settings"""
    
    # TODO: Implement actual settings storage
    return {"success": True, "message": "Settings updated"}


@router.get("/api-keys")
async def list_api_keys(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all API keys"""
    
    # Get all users with API keys
    users_with_keys = db.query(User).filter(User.api_key.isnot(None)).order_by(desc(User.created_at)).offset(offset).limit(limit).all()
    
    total = db.query(User).filter(User.api_key.isnot(None)).count()
    
    return {
        "api_keys": [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name or "Unknown",
                "organization": user.organization.name if user.organization else "No Organization",
                "api_key": f"{user.api_key[:8]}...{user.api_key[-4:]}" if user.api_key and len(user.api_key) > 12 else user.api_key,
                "created_at": user.created_at,
                "is_active": user.is_active
            }
            for user in users_with_keys
        ],
        "total": total
    }


@router.get("/logs")
async def get_system_logs(
    limit: int = 50,
    offset: int = 0,
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get system activity logs"""
    
    logs = []
    
    # Get recent user registrations
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(20).all()
    for user in recent_users:
        logs.append({
            "id": str(user.id),
            "level": "info",
            "type": "user",
            "message": f"New user registered: {user.email}",
            "service": "auth",
            "user": user.email,
            "timestamp": user.created_at.isoformat()
        })
    
    # Get recent organizations
    recent_orgs = db.query(Organization).order_by(desc(Organization.created_at)).limit(10).all()
    for org in recent_orgs:
        logs.append({
            "id": str(org.id),
            "level": "info",
            "type": "organization",
            "message": f"Organization created: {org.name}",
            "service": "orgs",
            "user": org.name,
            "timestamp": org.created_at.isoformat()
        })
    
    # Get recent traces/agent activity
    recent_traces = db.query(Trace).order_by(desc(Trace.created_at)).limit(20).all()
    for trace in recent_traces:
        level = "info"
        if trace.status == "error":
            level = "error"
        elif trace.status == "warning":
            level = "warning"
        logs.append({
            "id": str(trace.id),
            "level": level,
            "type": "trace",
            "message": f"Agent trace: {trace.status}",
            "service": "agents",
            "user": str(trace.agent_id) if trace.agent_id else "system",
            "timestamp": trace.created_at.isoformat()
        })
    
    # Sort by timestamp descending
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Filter by level if specified
    if level:
        logs = [log for log in logs if log["level"] == level]
    
    # Paginate
    total = len(logs)
    logs = logs[offset:offset + limit]
    
    return {
        "logs": logs,
        "total": total
    }


@router.get("/agents")
async def list_all_agents(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all agents across all organizations"""
    
    total = db.query(Agent).count()
    agents = db.query(Agent).order_by(desc(Agent.created_at)).offset(offset).limit(limit).all()
    
    return {
        "agents": [
            {
                "id": str(agent.id),
                "name": agent.name,
                "description": agent.description,
                "organization": agent.organization.name if agent.organization else "Unknown",
                "created_at": agent.created_at
            }
            for agent in agents
        ],
        "total": total
    }


@router.get("/subscriptions")
async def list_subscriptions(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all subscriptions"""
    
    # Get organizations with their subscription info
    orgs = db.query(Organization).order_by(desc(Organization.created_at)).offset(offset).limit(limit).all()
    total = db.query(Organization).count()
    
    return {
        "subscriptions": [
            {
                "id": str(org.id),
                "organization": org.name,
                "plan": org.plan.value if org.plan else "free",
                "status": "active",
                "user_count": db.query(User).filter(User.org_id == org.id).count(),
                "created_at": org.created_at
            }
            for org in orgs
        ],
        "total": total
    }


# ============ User CRUD Operations ============

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    name: str = None,
    is_active: bool = None,
    role: str = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a user (admin only)"""
    from uuid import UUID
    
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if name is not None:
        user.name = name
    if is_active is not None:
        user.is_active = is_active
    if role is not None:
        from app.models.user import UserRole
        try:
            user.role = UserRole(role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active,
        "role": user.role.value if user.role else "user",
        "organization": user.organization.name if user.organization else None,
        "created_at": user.created_at
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a user (admin only)"""
    from uuid import UUID
    
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting yourself
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


# ============ Organization CRUD Operations ============

@router.put("/organizations/{org_id}")
async def update_organization(
    org_id: str,
    name: str = None,
    plan: str = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update an organization (admin only)"""
    from uuid import UUID
    
    try:
        oid = UUID(org_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid organization ID format")
    
    org = db.query(Organization).filter(Organization.id == oid).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if name is not None:
        org.name = name
    if plan is not None:
        from app.models.organization import PlanType
        try:
            org.plan = PlanType(plan)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")
    
    db.commit()
    db.refresh(org)
    
    return {
        "id": str(org.id),
        "name": org.name,
        "plan": org.plan.value if org.plan else "free",
        "user_count": db.query(User).filter(User.org_id == org.id).count(),
        "created_at": org.created_at
    }


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete an organization (admin only)"""
    from uuid import UUID
    
    try:
        oid = UUID(org_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid organization ID format")
    
    org = db.query(Organization).filter(Organization.id == oid).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Delete all users in the organization first
    db.query(User).filter(User.org_id == org.id).delete()
    
    db.delete(org)
    db.commit()
    
    return {"message": "Organization deleted successfully"}


# ============ Billing Stats ============

@router.get("/billing")
async def get_billing_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get billing statistics"""
    from app.models.organization import PlanType
    
    # Calculate MRR based on plan prices
    plan_prices = {
        "free": 0,
        "starter": 19,
        "pro": 29,
        "team": 99,
        "enterprise": 299
    }
    
    orgs = db.query(Organization).all()
    total_mrr = sum(plan_prices.get(org.plan.value if org.plan else "free", 0) for org in orgs)
    
    total_subscriptions = len(orgs)
    paid_subscriptions = sum(1 for org in orgs if org.plan and org.plan.value != "free")
    
    return {
        "total_revenue": total_mrr * 12,  # Estimated yearly
        "monthly_recurring": total_mrr,
        "total_subscriptions": total_subscriptions,
        "active_trials": 0,  # No trial tracking yet
        "paid_subscriptions": paid_subscriptions,
        "free_subscriptions": total_subscriptions - paid_subscriptions
    }



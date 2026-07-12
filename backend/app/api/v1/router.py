"""
Main API router for v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    traces, tests, agents, health, users, insights, analytics, auth, api_keys,
    analysis, webhooks, emails, dashboard,
    admin, billing, organizations, mocks, regressions, health_monitoring, agent_graph, dodo_webhooks, contact,
    coordination
)

api_router = APIRouter()

# Public routes (no auth required)
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(contact.router, tags=["contact"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(dodo_webhooks.router, tags=["webhooks"])

# Protected routes (API key required)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(agents.router, tags=["agents"])
api_router.include_router(traces.router, tags=["traces"])
api_router.include_router(tests.router, tags=["tests"])
api_router.include_router(insights.router, tags=["insights"])
api_router.include_router(analytics.router, tags=["analytics"])

# AI Analysis routes
api_router.include_router(analysis.router, tags=["analysis"])
api_router.include_router(webhooks.router, tags=["webhooks"])

# Email routes
api_router.include_router(emails.router, tags=["emails"])

# Core Feature routes - Mocking
api_router.include_router(mocks.router, tags=["mocks"])

# Regression Detection routes
api_router.include_router(regressions.router, tags=["regressions"])

# Health Monitoring routes (JWT protected)
api_router.include_router(health_monitoring.router, tags=["health-monitoring"])

# JWT protected routes (bearer token required)
api_router.include_router(api_keys.router, tags=["api-keys"])

# Admin routes (admin role required)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Billing routes (user account required)
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])

# Organization routes (user account required)
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

# Agent Graph routes (multi-agent coordination analysis)
api_router.include_router(agent_graph.router, prefix="/agent-graph", tags=["agent-graph"])

# Phase 2: Coordination Intelligence routes
api_router.include_router(coordination.router, tags=["coordination"])

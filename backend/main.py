"""
AgentGuard API - Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.services.health_scheduler import health_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("🚀 Starting AgentGuard API...")
    print("⏰ Starting health check scheduler...")
    health_scheduler.start()
    print("✅ Health check scheduler started")
    yield
    # Shutdown
    print("🛑 Stopping health check scheduler...")
    health_scheduler.stop()
    print("👋 Shutting down AgentGuard API...")


app = FastAPI(
    title="AgentGuard API",
    description="""
    # AgentGuard - AI Agent Testing & Monitoring Platform
    
    AgentGuard provides comprehensive testing, monitoring, and observability for AI agents.
    
    ## Features
    
    - **Trace Collection**: Capture detailed execution traces from your AI agents
    - **Test Generation**: AI-powered test generation from execution patterns
    - **Health Monitoring**: Real-time health checks and uptime tracking
    - **Regression Detection**: Automatic performance degradation detection
    - **API Mocking**: Pre-built and custom API mocks for testing
    - **Analytics**: Rich insights and metrics from agent behavior
    
    ## Authentication
    
    Most endpoints require authentication via:
    - **API Key**: Include `X-API-Key` header with your API key
    - **JWT Token**: Include `Authorization: Bearer <token>` header (for user endpoints)
    
    ## Rate Limits
    
    Rate limits vary by subscription tier:
    - **Free**: 100 traces/min, 1000 queries/hour
    - **Pro**: 1000 traces/min, 10000 queries/hour
    - **Enterprise**: Custom limits
    
    ## Getting Started
    
    1. Sign up at https://agentguard.dev
    2. Create an API key from your dashboard
    3. Install SDK: `npm install @agentguard/sdk` or `pip install agentguard`
    4. Start sending traces!
    
    ## Support
    
    - Documentation: https://docs.agentguard.dev
    - Discord: https://discord.gg/agentguard
    - Email: support@overseex.com
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication and user management"
        },
        {
            "name": "agents",
            "description": "AI agent registration and management"
        },
        {
            "name": "traces",
            "description": "Execution trace collection and retrieval"
        },
        {
            "name": "tests",
            "description": "AI-powered test generation from traces"
        },
        {
            "name": "health",
            "description": "Agent health monitoring and uptime tracking"
        },
        {
            "name": "regressions",
            "description": "Performance regression detection and analysis"
        },
        {
            "name": "mocks",
            "description": "API mocking for testing and development"
        },
        {
            "name": "insights",
            "description": "AI-powered insights and analysis"
        },
        {
            "name": "analytics",
            "description": "Metrics, dashboards, and analytics"
        },
        {
            "name": "webhooks",
            "description": "Webhook configuration and delivery"
        },
        {
            "name": "billing",
            "description": "Subscription and billing management"
        },
        {
            "name": "admin",
            "description": "Admin-only endpoints (require admin role)"
        }
    ]
)

# Proxy headers middleware - trust X-Forwarded-Proto from nginx
# This ensures redirects use HTTPS when behind the proxy
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AgentGuard API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Check actual DB connection
        "redis": "connected",  # TODO: Check actual Redis connection
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

"""
Dashboard endpoints - simplified for quick testing
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/dashboard")


class DashboardStats(BaseModel):
    totalTraces: int
    successRate: float
    totalErrors: int
    avgDuration: float
    totalCost: float
    tracesToday: int
    changePercent: dict


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "totalTraces": 1247,
        "successRate": 94.3,
        "totalErrors": 71,
        "avgDuration": 1.4,
        "totalCost": 125.50,
        "tracesToday": 342,
        "changePercent": {
            "traces": 12,
            "success_rate": 2.1,
            "errors": -5
        }
    }


@router.get("/recent-traces")
async def get_recent_traces(limit: int = 10):
    """Get recent traces"""
    return {
        "traces": [
            {
                "id": "trace-1",
                "agent": "Agent A",
                "status": "success",
                "timestamp": "2 mins ago",
                "duration": "1.2s",
                "steps": 5,
                "confidence": 95
            }
        ]
    }


@router.get("/recent-errors")
async def get_recent_errors(limit: int = 10):
    """Get recent errors"""
    return {
        "errors": []
    }

"""
Analytics endpoints - simplified
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/analytics")


class AnalyticsResponse(BaseModel):
    metric: str
    value: float
    change: float


@router.get("/overview", response_model=List[AnalyticsResponse])
async def get_analytics_overview():
    """Get analytics overview"""
    return [
        {"metric": "total_traces", "value": 1234, "change": 12.5},
        {"metric": "success_rate", "value": 98.5, "change": 2.3},
        {"metric": "avg_duration", "value": 1.2, "change": -5.4}
    ]


@router.get("/traces")
async def get_trace_analytics():
    """Get trace analytics"""
    return {
        "total": 1234,
        "success": 1215,
        "failure": 19,
        "success_rate": 98.5
    }

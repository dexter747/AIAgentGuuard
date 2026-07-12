"""
Analysis endpoints - simplified
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/analysis")


class AnalysisRequest(BaseModel):
    trace_id: str


class AnalysisResponse(BaseModel):
    trace_id: str
    issues: list
    recommendations: list


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_trace(request: AnalysisRequest):
    """Analyze a trace"""
    return {
        "trace_id": request.trace_id,
        "issues": ["Slow response time", "High token usage"],
        "recommendations": ["Optimize prompt", "Use caching"]
    }

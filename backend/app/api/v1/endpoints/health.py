"""
Health check API endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_status():
    """Get health check status"""
    # TODO: Implement
    return {"status": "healthy"}

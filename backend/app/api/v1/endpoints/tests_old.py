"""
Tests API endpoints
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()


class TestResponse(BaseModel):
    id: str
    name: str
    agent_id: str
    agent_name: str
    status: str
    input: str
    duration_ms: int = 0
    last_run: str = None


@router.get("/", response_model=List[TestResponse])
async def list_tests():
    """List all tests"""
    return [
        {
            "id": "1",
            "name": "Customer Query Response",
            "agent_id": "agent-1",
            "agent_name": "Support Agent",
            "status": "passed",
            "input": "What is your return policy?",
            "duration_ms": 1250,
            "last_run": "2026-01-23T10:30:00Z"
        }
    ]


@router.post("/run")
async def run_tests():
    """Run tests"""
    return {"status": "running", "id": "run-123"}


@router.get("/{test_id}")
async def get_test(test_id: str):
    """Get test by ID"""
    return {
        "id": test_id,
        "name": "Test",
        "status": "passed"
    }


@router.post("/")
async def create_test(name: str, agent_id: str):
    """Create a new test"""
    return {
        "id": "new",
        "name": name,
        "agent_id": agent_id,
        "status": "created"
    }

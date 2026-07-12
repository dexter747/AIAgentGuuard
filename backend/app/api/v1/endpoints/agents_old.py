"""
Agents API endpoints
"""
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/agents")


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    type: str
    tracesTotal: int
    tracesToday: int
    successRate: float
    avgLatency: float
    costToday: float
    lastActive: str
    tools: List[str]


@router.get("/", response_model=List[AgentResponse])
async def list_agents():
    """List all agents"""
    # Mock data for now
    return [
        {
            "id": "1",
            "name": "Customer Support Bot",
            "description": "Handles customer inquiries and support tickets",
            "status": "healthy",
            "type": "multi",
            "tracesTotal": 15420,
            "tracesToday": 847,
            "successRate": 97.2,
            "avgLatency": 1.24,
            "costToday": 12.45,
            "lastActive": "2 minutes ago",
            "tools": ["openai", "zendesk", "slack"]
        }
    ]


@router.post("/")
async def create_agent(name: str, description: str):
    """Create a new agent"""
    return {
        "id": "new",
        "name": name,
        "description": description,
        "status": "created"
    }


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent by ID"""
    return {
        "id": agent_id,
        "name": "Agent",
        "status": "healthy"
    }

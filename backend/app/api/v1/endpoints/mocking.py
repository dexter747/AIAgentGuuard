"""
Tool Mocking API Endpoints
Configure and manage tool mocks for agent testing.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.trace import Trace
from app.models.agent import Agent
from app.models.user import User
from app.services.mock_engine import MockEngine, mock_tools

router = APIRouter(prefix="/mocking")

# In-memory mock configurations (in production, store in Redis or DB)
mock_configs: Dict[str, Dict] = {}


class MockConfigCreate(BaseModel):
    tool_name: str
    default_response: Optional[Dict[str, Any]] = None
    responses: Optional[List[Dict[str, Any]]] = None  # Conditional responses
    failure_mode: Optional[Dict[str, Any]] = None


class MockConfigResponse(BaseModel):
    id: str
    tool_name: str
    default_response: Optional[Dict[str, Any]]
    responses: Optional[List[Dict[str, Any]]]
    failure_mode: Optional[Dict[str, Any]]
    created_at: str


class LearnFromTracesRequest(BaseModel):
    trace_ids: List[str]


class MockTestRequest(BaseModel):
    tool_name: str
    method: Optional[str] = None
    args: Optional[Dict[str, Any]] = None


@router.get("/templates")
async def get_mock_templates(
    current_user: User = Depends(get_current_user)
):
    """
    Get available mock templates for common tools.
    
    Returns pre-configured mock responses for popular APIs
    like OpenAI, Stripe, Google Calendar, etc.
    """
    engine = MockEngine()
    
    templates = {}
    for tool_name, methods in engine.TOOL_TEMPLATES.items():
        templates[tool_name] = {
            "methods": list(methods.keys()),
            "sample_response": methods[list(methods.keys())[0]].body if methods else None
        }
    
    return {
        "templates": templates,
        "supported_tools": list(engine.TOOL_TEMPLATES.keys()),
        "total_templates": len(engine.TOOL_TEMPLATES)
    }


@router.post("/configure")
async def configure_mock(
    config: MockConfigCreate,
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configure a mock for a specific tool.
    
    Set up default responses, conditional responses, or failure modes
    for testing agent behavior with mocked API calls.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Store configuration
    config_id = f"{agent_id}_{config.tool_name}"
    mock_configs[config_id] = {
        "id": config_id,
        "agent_id": agent_id,
        "tool_name": config.tool_name,
        "default_response": config.default_response,
        "responses": config.responses,
        "failure_mode": config.failure_mode,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "id": config_id,
        "message": f"Mock configured for {config.tool_name}",
        "config": mock_configs[config_id]
    }


@router.get("/configs/{agent_id}")
async def get_mock_configs(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all mock configurations for an agent.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get configs for this agent
    agent_configs = [
        config for config_id, config in mock_configs.items()
        if config.get("agent_id") == agent_id
    ]
    
    return {
        "agent_id": agent_id,
        "configs": agent_configs,
        "total": len(agent_configs)
    }


@router.post("/learn-from-traces")
async def learn_from_traces(
    request: LearnFromTracesRequest,
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Learn mock responses from existing traces.
    
    Analyzes the provided traces to extract tool calls and their
    responses, then configures mocks to replay those responses.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Fetch traces
    traces = db.query(Trace).filter(
        Trace.id.in_(request.trace_ids),
        Trace.agent_id == agent_id
    ).all()
    
    if not traces:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No traces found"
        )
    
    # Learn from traces
    engine = MockEngine()
    tools_learned = set()
    responses_learned = 0
    
    for trace in traces:
        trace_data = trace.trace_data if isinstance(trace.trace_data, dict) else {}
        engine.learn_from_trace(trace_data)
        
        # Extract tool names
        tool_calls = trace_data.get("tool_calls", [])
        if not tool_calls and "steps" in trace_data:
            tool_calls = [s for s in trace_data["steps"] if s.get("type") == "tool_call"]
        if not tool_calls and "metadata" in trace_data:
            tool_calls = trace_data["metadata"].get("tool_calls", [])
        
        for call in tool_calls:
            tool_name = call.get("tool", call.get("name"))
            if tool_name:
                tools_learned.add(tool_name)
                responses_learned += 1
    
    return {
        "message": "Mocks learned from traces",
        "traces_analyzed": len(traces),
        "tools_learned": list(tools_learned),
        "responses_learned": responses_learned
    }


@router.post("/inject-failure")
async def inject_failure(
    tool_name: str,
    error_type: str = "server_error",
    error_code: Optional[int] = None,
    probability: float = 1.0,
    agent_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inject a failure for a specific tool.
    
    Use this to test how your agent handles various error conditions
    like timeouts, rate limits, or server errors.
    
    Error types:
    - timeout: Request timeout (408)
    - rate_limit: Too many requests (429)
    - server_error: Internal server error (500)
    - connection_error: Service unavailable (503)
    - not_found: Resource not found (404)
    - unauthorized: Authentication failed (401)
    """
    valid_error_types = [
        "timeout", "rate_limit", "server_error", 
        "connection_error", "not_found", "unauthorized", "forbidden"
    ]
    
    if error_type not in valid_error_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid error type. Must be one of: {valid_error_types}"
        )
    
    if not 0 <= probability <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Probability must be between 0 and 1"
        )
    
    # Store failure configuration
    config_id = f"{agent_id or 'global'}_{tool_name}_failure"
    mock_configs[config_id] = {
        "id": config_id,
        "tool_name": tool_name,
        "failure_mode": {
            "type": error_type,
            "code": error_code,
            "probability": probability
        },
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "message": f"Failure injection configured for {tool_name}",
        "error_type": error_type,
        "probability": probability,
        "config_id": config_id
    }


@router.delete("/clear-failures")
async def clear_failures(
    agent_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Clear all failure injections.
    """
    # Remove failure configs
    keys_to_remove = [
        key for key in mock_configs
        if "_failure" in key and (not agent_id or agent_id in key)
    ]
    
    for key in keys_to_remove:
        del mock_configs[key]
    
    return {
        "message": "Failure injections cleared",
        "configs_removed": len(keys_to_remove)
    }


@router.post("/test-mock")
async def test_mock(
    request: MockTestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Test a mock configuration.
    
    Execute a mock call to verify the configuration is working correctly.
    """
    engine = MockEngine()
    mock = engine.get_mock(request.tool_name)
    
    try:
        if request.args:
            response = mock(**request.args)
        else:
            response = mock()
        
        return {
            "tool": request.tool_name,
            "response": response,
            "mock_called": mock.called,
            "call_count": mock.call_count
        }
    except Exception as e:
        return {
            "tool": request.tool_name,
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.get("/cost-savings")
async def get_cost_savings(
    current_user: User = Depends(get_current_user)
):
    """
    Get estimated cost savings from using mocks.
    
    Calculates how much money has been saved by mocking API calls
    instead of making real requests during testing.
    """
    # This would typically aggregate from test runs
    # For now, return sample data
    return {
        "total_saved": 125.50,
        "breakdown": {
            "openai": {"calls": 3500, "cost_per_call": 0.03, "saved": 105.00},
            "stripe": {"calls": 500, "cost_per_call": 0.01, "saved": 5.00},
            "sendgrid": {"calls": 1500, "cost_per_call": 0.001, "saved": 1.50},
            "twilio": {"calls": 200, "cost_per_call": 0.0075, "saved": 1.50},
            "google_calendar": {"calls": 5000, "cost_per_call": 0.0001, "saved": 0.50},
            "slack": {"calls": 12000, "cost_per_call": 0.0001, "saved": 1.20}
        },
        "period": "last_30_days",
        "total_mock_calls": 22700
    }

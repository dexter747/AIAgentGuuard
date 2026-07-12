"""
Test Generation API Endpoints
Automatically generate tests from agent traces.

Supports two modes:
1. Template-based generation (fast, deterministic)
2. AI-powered generation (uses LLM for intelligent test creation)
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.trace import Trace
from app.models.agent import Agent
from app.models.test import Test
from app.models.user import User
from app.services.test_generator import TestGenerator
from app.services.ai_test_generator import AITestGenerator
from app.services.smart_mock_generator import smart_mock_generator
from app.services.dodo_payments import check_usage_limit

router = APIRouter(prefix="/test-generation")


class GenerateTestRequest(BaseModel):
    trace_id: str
    test_name: Optional[str] = None
    use_ai: bool = False  # Use LLM for intelligent generation
    context: Optional[str] = None  # Additional context for AI


class GenerateTestSuiteRequest(BaseModel):
    agent_id: str
    trace_ids: Optional[List[str]] = None  # If None, use recent traces
    suite_name: Optional[str] = None
    max_traces: int = 20
    use_ai: bool = False  # Use LLM for intelligent generation
    include_edge_cases: bool = True
    include_mocks: bool = True


class GeneratedTest(BaseModel):
    name: str
    code: str
    source_trace_id: str
    agent_id: str
    llm_generated: bool = False
    assertions: List[str] = []
    mocks_needed: List[str] = []


class GeneratedTestSuite(BaseModel):
    suite_name: str
    agent_name: str
    total_tests: int
    code: str
    tests: List[Dict[str, Any]]
    coverage: Optional[Dict[str, Any]] = None
    edge_cases: Optional[List[Dict[str, Any]]] = None


class GenerateMocksRequest(BaseModel):
    tool_names: List[str]
    include_errors: bool = True
    learn_from_agent_id: Optional[str] = None


@router.post("/from-trace", response_model=GeneratedTest)
async def generate_test_from_trace(
    request: GenerateTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a single test from a trace.
    
    Takes a trace ID and generates a pytest-compatible test case
    that can be used to validate agent behavior.
    """
    # Check plan limits before creating
    can_create, current_count, limit = check_usage_limit(current_user, "tests", db)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Test limit reached ({current_count}/{limit}). Please upgrade your plan to generate more tests."
        )
    
    # Fetch the trace
    trace = db.query(Trace).join(Agent).filter(
        Trace.id == request.trace_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )
    
    # Get agent info
    agent = db.query(Agent).filter(Agent.id == trace.agent_id).first()
    
    # Generate test
    generator = TestGenerator()
    
    # Parse trace data
    trace_data = trace.trace_data if isinstance(trace.trace_data, dict) else {}
    trace_data.update({
        "id": str(trace.id),
        "status": trace.status or "success",
        "duration_ms": trace.total_duration_ms or 0,
        "created_at": trace.created_at.isoformat() if trace.created_at else None
    })
    
    test_code = generator.generate_tests_from_trace(
        trace_data=trace_data,
        agent_name=agent.name if agent else "Agent",
        test_name=request.test_name
    )
    
    # Create test name
    test_name = request.test_name or f"test_from_trace_{str(trace.id)[:8]}"
    
    return GeneratedTest(
        name=test_name,
        code=test_code,
        source_trace_id=str(trace.id),
        agent_id=str(trace.agent_id)
    )


@router.post("/suite", response_model=GeneratedTestSuite)
async def generate_test_suite(
    request: GenerateTestSuiteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a complete test suite from multiple traces.
    
    Analyzes traces for an agent and generates a comprehensive
    test suite covering success cases, error handling, and edge cases.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == request.agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Fetch traces
    if request.trace_ids:
        traces = db.query(Trace).filter(
            Trace.id.in_(request.trace_ids),
            Trace.agent_id == agent.id
        ).all()
    else:
        # Get recent traces
        traces = db.query(Trace).filter(
            Trace.agent_id == agent.id
        ).order_by(Trace.created_at.desc()).limit(request.max_traces).all()
    
    if not traces:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No traces found for this agent"
        )
    
    # Convert traces to dict format
    trace_dicts = []
    for trace in traces:
        trace_data = trace.trace_data if isinstance(trace.trace_data, dict) else {}
        trace_data.update({
            "id": str(trace.id),
            "status": trace.status or "success",
            "duration_ms": trace.total_duration_ms or 0,
            "created_at": trace.created_at.isoformat() if trace.created_at else None
        })
        trace_dicts.append(trace_data)
    
    # Generate test suite
    generator = TestGenerator()
    suite_code = generator.generate_test_suite_from_traces(
        traces=trace_dicts,
        agent_name=agent.name,
        suite_name=request.suite_name
    )
    
    # Parse generated tests for response
    tests_info = []
    success_count = len([t for t in trace_dicts if t.get("status") == "success"])
    error_count = len([t for t in trace_dicts if t.get("status") in ["error", "failed"]])
    
    tests_info.append({"type": "success", "count": min(success_count, 10)})
    tests_info.append({"type": "error_handling", "count": min(error_count, 5)})
    tests_info.append({"type": "edge_case", "count": 5})
    
    return GeneratedTestSuite(
        suite_name=request.suite_name or f"Test{agent.name.replace(' ', '')}Suite",
        agent_name=agent.name,
        total_tests=sum(t["count"] for t in tests_info),
        code=suite_code,
        tests=tests_info
    )


@router.post("/save")
async def save_generated_test(
    test_data: GeneratedTest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a generated test to the database.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == test_data.agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Create test record
    test = Test(
        agent_id=test_data.agent_id,
        name=test_data.name,
        code=test_data.code,
        source_trace_id=test_data.source_trace_id,
        is_active=True
    )
    
    db.add(test)
    db.commit()
    db.refresh(test)
    
    return {
        "id": str(test.id),
        "name": test.name,
        "agent_id": str(test.agent_id),
        "created_at": test.created_at.isoformat() if test.created_at else "",
        "message": "Test saved successfully"
    }


@router.post("/regression-test")
async def generate_regression_test(
    trace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a regression test from a baseline trace.
    
    Creates a test that compares agent behavior against the baseline,
    useful for catching regressions after prompt or code changes.
    """
    # Fetch the trace
    trace = db.query(Trace).join(Agent).filter(
        Trace.id == trace_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )
    
    agent = db.query(Agent).filter(Agent.id == trace.agent_id).first()
    
    # Parse trace data
    trace_data = trace.trace_data if isinstance(trace.trace_data, dict) else {}
    trace_data.update({
        "id": str(trace.id),
        "status": trace.status or "success",
        "created_at": trace.created_at.isoformat() if trace.created_at else None
    })
    
    # Generate regression test
    generator = TestGenerator()
    test_code = generator.generate_regression_test(
        baseline_trace=trace_data,
        agent_name=agent.name if agent else "Agent"
    )
    
    return {
        "name": f"regression_test_{str(trace.id)[:8]}",
        "code": test_code,
        "baseline_trace_id": str(trace.id),
        "agent_id": str(trace.agent_id),
        "type": "regression"
    }


@router.post("/ai-generate")
async def ai_generate_test(
    request: GenerateTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a test using AI (LLM-powered).
    
    Uses OpenAI or Anthropic to intelligently analyze the trace
    and generate comprehensive, semantically meaningful tests.
    
    Features:
    - Understands agent behavior semantically
    - Generates meaningful assertions
    - Identifies edge cases
    - Creates appropriate mocks
    
    Note: Requires OpenAI or Anthropic API key configured.
    Falls back to template-based generation if unavailable.
    """
    # Check plan limits
    can_create, current_count, limit = check_usage_limit(current_user, "tests", db)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Test limit reached ({current_count}/{limit}). Upgrade to generate more."
        )
    
    # Fetch trace
    trace = db.query(Trace).join(Agent).filter(
        Trace.id == request.trace_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )
    
    agent = db.query(Agent).filter(Agent.id == trace.agent_id).first()
    
    # Parse trace data
    trace_data = trace.trace_data if isinstance(trace.trace_data, dict) else {}
    trace_data.update({
        "id": str(trace.id),
        "input_data": trace_data.get("input", {}),
        "output_data": trace_data.get("output", {}),
        "status": trace.status or "success",
        "duration_ms": trace.total_duration_ms or 0,
        "created_at": trace.created_at.isoformat() if trace.created_at else None
    })
    
    # Initialize AI generator
    ai_generator = AITestGenerator(
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        fallback_to_template=True
    )
    
    # Generate test
    result = ai_generator.generate_test_from_trace(
        trace=trace_data,
        agent_name=agent.name if agent else "Agent",
        context=request.context
    )
    
    return {
        "name": result.get("test_name", f"test_{str(trace.id)[:8]}"),
        "code": result.get("code", ""),
        "source_trace_id": str(trace.id),
        "agent_id": str(trace.agent_id),
        "llm_generated": result.get("llm_generated", False),
        "assertions": result.get("assertions", []),
        "mocks_needed": result.get("mocks_needed", []),
        "description": result.get("description", "")
    }


@router.post("/ai-suite")
async def ai_generate_test_suite(
    request: GenerateTestSuiteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a complete AI-powered test suite.
    
    Analyzes multiple traces to create a comprehensive test suite
    with coverage analysis and edge case identification.
    """
    # Verify agent access
    agent = db.query(Agent).filter(
        Agent.id == request.agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Fetch traces
    if request.trace_ids:
        traces = db.query(Trace).filter(
            Trace.id.in_(request.trace_ids),
            Trace.agent_id == agent.id
        ).all()
    else:
        traces = db.query(Trace).filter(
            Trace.agent_id == agent.id
        ).order_by(Trace.created_at.desc()).limit(request.max_traces).all()
    
    if not traces:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No traces found for this agent"
        )
    
    # Convert traces
    trace_dicts = []
    for trace in traces:
        trace_data = trace.trace_data if isinstance(trace.trace_data, dict) else {}
        trace_data.update({
            "id": str(trace.id),
            "input_data": trace_data.get("input", {}),
            "output_data": trace_data.get("output", {}),
            "status": trace.status or "success",
            "duration_ms": trace.total_duration_ms or 0
        })
        trace_dicts.append(trace_data)
    
    # Initialize AI generator
    ai_generator = AITestGenerator(fallback_to_template=True)
    
    # Generate suite
    result = ai_generator.generate_test_suite(
        traces=trace_dicts,
        agent_name=agent.name,
        max_tests=request.max_traces
    )
    
    # Identify edge cases if requested
    edge_cases = None
    if request.include_edge_cases:
        edge_cases = ai_generator.identify_edge_cases(trace_dicts)
    
    return {
        "suite_name": request.suite_name or f"Test{agent.name.replace(' ', '')}Suite",
        "agent_name": agent.name,
        "total_tests": result.get("test_count", 0),
        "code": result.get("code", ""),
        "tests": result.get("tests", []),
        "coverage": result.get("coverage"),
        "edge_cases": edge_cases,
        "summary": result.get("summary", "")
    }


@router.post("/generate-mocks")
async def generate_mocks(
    request: GenerateMocksRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate smart mocks for external tool/API calls.
    
    Can learn patterns from existing traces to create
    more realistic mock responses.
    """
    # Learn from traces if agent specified
    if request.learn_from_agent_id:
        agent = db.query(Agent).filter(
            Agent.id == request.learn_from_agent_id,
            Agent.org_id == current_user.org_id
        ).first()
        
        if agent:
            traces = db.query(Trace).filter(
                Trace.agent_id == agent.id
            ).order_by(Trace.created_at.desc()).limit(100).all()
            
            trace_dicts = [
                trace.trace_data if isinstance(trace.trace_data, dict) else {}
                for trace in traces
            ]
            
            # Learn patterns from traces
            patterns_learned = smart_mock_generator.learn_from_traces(trace_dicts)
    
    # Generate mock suite
    mock_suite = smart_mock_generator.generate_mock_suite(
        tool_names=request.tool_names,
        include_errors=request.include_errors
    )
    
    # Export as code
    mock_code = smart_mock_generator.export_mocks_as_code(mock_suite)
    
    return {
        "mocks": mock_suite,
        "code": mock_code,
        "tools_covered": len(mock_suite),
        "patterns_stats": smart_mock_generator.get_pattern_stats()
    }


@router.get("/edge-cases/{agent_id}")
async def identify_edge_cases(
    agent_id: str,
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze traces to identify potential edge cases for testing.
    
    Returns traces that might represent edge cases based on:
    - Input patterns (empty, very long, special chars)
    - Execution patterns (slow, fast, high tokens)
    - Error patterns
    """
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    traces = db.query(Trace).filter(
        Trace.agent_id == agent.id
    ).order_by(Trace.created_at.desc()).limit(limit).all()
    
    trace_dicts = []
    for trace in traces:
        trace_data = trace.trace_data if isinstance(trace.trace_data, dict) else {}
        trace_data.update({
            "id": str(trace.id),
            "input_data": trace_data.get("input", {}),
            "status": trace.status,
            "duration_ms": trace.total_duration_ms,
            "error_message": trace.error_message
        })
        trace_dicts.append(trace_data)
    
    ai_generator = AITestGenerator(fallback_to_template=True)
    edge_cases = ai_generator.identify_edge_cases(trace_dicts)
    
    return {
        "agent_id": agent_id,
        "traces_analyzed": len(trace_dicts),
        "edge_cases_found": len(edge_cases),
        "edge_cases": edge_cases[:50]  # Limit response size
    }


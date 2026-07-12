"""
Test management endpoints with database integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import re

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.test import Test, TestRun
from app.models.agent import Agent
from app.models.user import User
from app.models.trace import Trace
from app.services.test_generator import test_generator
from app.services.dodo_payments import check_usage_limit

router = APIRouter(prefix="/tests")


# Request/Response Models
class TestCreate(BaseModel):
    name: str
    agent_id: str
    code: str
    source_trace_id: Optional[str] = None


class TestGenerateRequest(BaseModel):
    trace_id: str
    test_name: Optional[str] = None


class TestGenerateResponse(BaseModel):
    generated_code: str
    test_name: str
    trace_id: str
    agent_name: str


class TestResponse(BaseModel):
    id: str
    name: str
    agent_id: str
    agent_name: Optional[str]
    code: str
    is_active: bool
    created_at: str
    last_run: Optional[dict] = None


class TestRunResponse(BaseModel):
    id: str
    test_id: str
    status: str
    duration_ms: Optional[int]
    error_message: Optional[str]
    created_at: str


@router.get("/", response_model=List[TestResponse])
async def list_tests(
    agent_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all tests for the current organization"""
    
    # Get tests through agents
    query = db.query(Test).join(Agent).filter(
        Agent.org_id == current_user.org_id
    )
    
    if agent_id:
        query = query.filter(Test.agent_id == agent_id)
    
    tests = query.all()
    
    result = []
    for test in tests:
        agent = db.query(Agent).filter(Agent.id == test.agent_id).first()
        
        # Get last test run
        last_run = db.query(TestRun).filter(
            TestRun.test_id == test.id
        ).order_by(TestRun.created_at.desc()).first()
        
        last_run_data = None
        if last_run:
            last_run_data = {
                "id": str(last_run.id),
                "status": last_run.status,
                "duration_ms": last_run.duration_ms,
                "created_at": last_run.created_at.isoformat() if last_run.created_at else ""
            }
        
        result.append(TestResponse(
            id=str(test.id),
            name=test.name,
            agent_id=str(test.agent_id),
            agent_name=agent.name if agent else "Unknown",
            code=test.code,
            is_active=test.is_active if test.is_active is not None else True,
            created_at=test.created_at.isoformat() if test.created_at else "",
            last_run=last_run_data
        ))
    
    return result


@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(
    test_data: TestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new test"""
    
    # Check plan limits before creating
    can_create, current_count, limit = check_usage_limit(current_user, "tests", db)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Test limit reached ({current_count}/{limit}). Please upgrade your plan to create more tests."
        )
    
    # Verify agent belongs to user's organization
    agent = db.query(Agent).filter(
        Agent.id == test_data.agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Create test
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
    
    return TestResponse(
        id=str(test.id),
        name=test.name,
        agent_id=str(test.agent_id),
        agent_name=agent.name,
        code=test.code,
        is_active=test.is_active if test.is_active is not None else True,
        created_at=test.created_at.isoformat() if test.created_at else "",
        last_run=None
    )


@router.get("/{test_id}", response_model=TestResponse)
async def get_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific test"""
    
    test = db.query(Test).join(Agent).filter(
        Test.id == test_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    agent = db.query(Agent).filter(Agent.id == test.agent_id).first()
    
    # Get last test run
    last_run = db.query(TestRun).filter(
        TestRun.test_id == test.id
    ).order_by(TestRun.created_at.desc()).first()
    
    last_run_data = None
    if last_run:
        last_run_data = {
            "id": str(last_run.id),
            "status": last_run.status,
            "duration_ms": last_run.duration_ms,
            "created_at": last_run.created_at.isoformat() if last_run.created_at else ""
        }
    
    return TestResponse(
        id=str(test.id),
        name=test.name,
        agent_id=str(test.agent_id),
        agent_name=agent.name if agent else "Unknown",
        code=test.code,
        is_active=test.is_active if test.is_active is not None else True,
        created_at=test.created_at.isoformat() if test.created_at else "",
        last_run=last_run_data
    )


@router.post("/{test_id}/run", response_model=TestRunResponse)
async def run_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run a test"""
    
    test = db.query(Test).join(Agent).filter(
        Test.id == test_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    # Execute the test
    # TODO: Implement actual test execution in sandbox
    test_run = TestRun(
        test_id=test.id,
        status="pending",
        duration_ms=None,
        error_message=None,
        logs="Test queued for execution"
    )
    
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    return TestRunResponse(
        id=str(test_run.id),
        test_id=str(test_run.test_id),
        status=test_run.status or "unknown",
        duration_ms=test_run.duration_ms,
        error_message=test_run.error_message,
        created_at=test_run.created_at.isoformat() if test_run.created_at else ""
    )


@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a test"""
    
    test = db.query(Test).join(Agent).filter(
        Test.id == test_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    db.delete(test)
    db.commit()
    
    return None


@router.post("/generate", response_model=TestGenerateResponse)
async def generate_test_from_trace(
    request: TestGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate pytest code from an execution trace
    
    This endpoint uses AI-powered analysis to convert agent execution traces
    into pytest-compatible test cases with proper assertions and mocks.
    """
    # Verify trace belongs to user's organization
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
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    try:
        # Generate test code using TestGenerator service
        generated_code = test_generator.generate_tests_from_trace(
            trace_data=trace.trace_data,
            agent_name=agent.name,
            test_name=request.test_name
        )
        
        # Extract test name from generated code
        test_name_match = re.search(r'def (test_\w+)\(', generated_code)
        extracted_test_name = test_name_match.group(1) if test_name_match else "test_generated"
        
        return TestGenerateResponse(
            generated_code=generated_code,
            test_name=extracted_test_name,
            trace_id=str(trace.id),
            agent_name=agent.name
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test: {str(e)}"
        )


@router.post("/generate-suite", response_model=TestGenerateResponse)
async def generate_test_suite_from_agent(
    agent_id: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a complete test suite from recent traces of an agent
    
    Analyzes multiple traces to create a comprehensive test suite including:
    - Success cases
    - Error handling
    - Edge cases
    - Regression tests
    """
    # Verify agent belongs to user's organization
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get recent traces
    traces = db.query(Trace).filter(
        Trace.agent_id == agent_id
    ).order_by(Trace.created_at.desc()).limit(limit).all()
    
    if not traces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No traces found for this agent"
        )
    
    try:
        # Convert to list of dicts
        trace_data_list = [trace.trace_data for trace in traces]
        
        # Generate test suite
        generated_code = test_generator.generate_test_suite_from_traces(
            traces=trace_data_list,
            agent_name=agent.name
        )
        
        return TestGenerateResponse(
            generated_code=generated_code,
            test_name=f"Test{agent.name}Suite",
            trace_id=str(traces[0].id),
            agent_name=agent.name
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test suite: {str(e)}"
        )


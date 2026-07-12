"""
Mock management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.mock_engine import mock_engine, ToolMock
from app.mocks.prebuilt_mocks import get_prebuilt_mock, list_available_mocks

router = APIRouter(prefix="/mocks")


# Request/Response Models
class MockCreate(BaseModel):
    tool_name: str
    response: Any
    behavior: str = "success"  # success, error, timeout, rate_limit
    conditions: Optional[Dict[str, Any]] = None


class MockResponse(BaseModel):
    tool_name: str
    response: Any
    response_data: Any  # Alias for frontend compatibility
    behavior: str
    call_count: int
    created_at: str
    is_active: bool = True  # For frontend compatibility
    last_called: Optional[str] = None  # For frontend compatibility


class MockCallHistory(BaseModel):
    tool_name: str
    input: Any
    input_data: Any  # Alias for frontend compatibility
    response: Any
    output_data: Any  # Alias for frontend compatibility
    timestamp: str
    call_number: int
    success: bool = True  # For frontend compatibility


class PrebuiltMockInfo(BaseModel):
    name: str
    category: str
    description: str
    example_response: Dict[str, Any]


def _tool_mock_to_response(tool_name: str, mock: ToolMock) -> MockResponse:
    """Convert a ToolMock to API response format"""
    response_body = {}
    behavior = "success"
    
    if mock.default_response:
        response_body = mock.default_response.body or {}
    elif mock.responses:
        first_response = mock.responses[0].get("response")
        if first_response:
            response_body = first_response.body or {}
    
    if mock.failure_mode:
        behavior = mock.failure_mode.get("error_type", "error")
    
    # Determine is_active based on whether it has a failure mode
    is_active = not bool(mock.failure_mode) or mock.failure_mode.get("error_type") != "disabled"
    
    # Get last called time from call history
    last_called = None
    if mock.calls:
        last_called = mock.calls[-1].timestamp.isoformat()
    
    return MockResponse(
        tool_name=tool_name,
        response=response_body,
        response_data=response_body,  # Alias for frontend
        behavior=behavior,
        call_count=mock.call_count,
        created_at=datetime.utcnow().isoformat(),
        is_active=is_active,
        last_called=last_called
    )


@router.get("/")
async def list_mocks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all registered mocks"""
    mocks = []
    
    for tool_name, mock in mock_engine.mocks.items():
        mocks.append(_tool_mock_to_response(tool_name, mock))
    
    return {"mocks": mocks}  # Wrap in object for frontend compatibility


@router.post("/", response_model=MockResponse, status_code=status.HTTP_201_CREATED)
async def create_mock(
    mock_data: MockCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new mock"""
    # Get or create the mock
    mock = mock_engine.get_mock(mock_data.tool_name)
    
    # Set the response based on behavior
    if mock_data.behavior == "success":
        mock.set_default_response(mock_data.response)
    elif mock_data.behavior in ["error", "timeout", "rate_limit", "server_error"]:
        mock.inject_failure(
            error_type=mock_data.behavior,
            error_message=mock_data.response.get("message", "Mock failure") if isinstance(mock_data.response, dict) else "Mock failure"
        )
    else:
        mock.set_default_response(mock_data.response)
    
    return _tool_mock_to_response(mock_data.tool_name, mock)


@router.get("/prebuilt", response_model=List[PrebuiltMockInfo])
async def list_prebuilt_mocks(
    current_user: User = Depends(get_current_user)
):
    """List available pre-built mocks"""
    from app.mocks.prebuilt_mocks import PREBUILT_MOCKS
    
    # Categorize mocks
    mock_categories = {
        'stripe_': 'Payment',
        'sendgrid_': 'Email',
        'google_calendar_': 'Calendar',
        'slack_': 'Communication',
        'twilio_': 'Communication',
        'github_': 'Development',
        'openai_': 'AI',
        'aws_': 'Cloud'
    }
    
    prebuilt_mocks = []
    for tool_name, mock_factory in PREBUILT_MOCKS.items():
        # Determine category
        category = 'Other'
        for prefix, cat in mock_categories.items():
            if tool_name.startswith(prefix):
                category = cat
                break
        
        # Get example response by calling the factory function
        try:
            mock_instance = mock_factory()
            if hasattr(mock_instance, 'default_response') and mock_instance.default_response:
                if hasattr(mock_instance.default_response, 'body'):
                    example_response = mock_instance.default_response.body
                else:
                    example_response = {}
            else:
                example_response = {}
            
            # Ensure it's a dictionary
            if not isinstance(example_response, dict):
                example_response = {}
        except Exception as e:
            print(f"Error getting mock instance for {tool_name}: {e}")
            example_response = {}
        
        # Generate description from tool name
        description = tool_name.replace('_', ' ').title()
        
        prebuilt_mocks.append(PrebuiltMockInfo(
            name=tool_name,
            category=category,
            description=description,
            example_response=example_response
        ))
    
    return prebuilt_mocks


@router.post("/prebuilt/{tool_name}", response_model=MockResponse)
async def load_prebuilt_mock(
    tool_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Load a pre-built mock"""
    prebuilt_mock = get_prebuilt_mock(tool_name)
    
    if not prebuilt_mock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pre-built mock '{tool_name}' not found"
        )
    
    # Register the pre-built mock by copying its configuration
    mock = mock_engine.get_mock(tool_name)
    
    # Copy the default response from the prebuilt mock
    if prebuilt_mock.default_response:
        mock.set_default_response(
            prebuilt_mock.default_response.body,
            prebuilt_mock.default_response.status_code
        )
    
    # Copy any configured responses
    for resp_config in prebuilt_mock.responses:
        response_obj = resp_config.get("response")
        if response_obj:
            mock.set_response(
                response_obj.body,
                response_obj.status_code,
                condition=resp_config.get("condition"),
                match_args=resp_config.get("match_args")
            )
    
    return _tool_mock_to_response(tool_name, mock)


@router.get("/{tool_name}/history")
async def get_mock_call_history(
    tool_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get call history for a mock"""
    if tool_name not in mock_engine.mocks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mock '{tool_name}' not found"
        )
    
    mock = mock_engine.mocks[tool_name]
    history = []
    
    for i, call in enumerate(mock.calls):
        input_data = {"args": call.args, "kwargs": call.kwargs}
        history.append(MockCallHistory(
            tool_name=call.tool_name,
            input=input_data,
            input_data=input_data,  # Alias for frontend
            response=call.response,
            output_data=call.response,  # Alias for frontend
            timestamp=call.timestamp.isoformat(),
            call_number=i + 1,
            success=True  # Default to success for frontend
        ))
    
    return {"history": history}  # Wrap in object for frontend compatibility


@router.post("/{tool_name}/toggle", response_model=MockResponse)
async def toggle_mock(
    tool_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle a mock's active state"""
    if tool_name not in mock_engine.mocks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mock '{tool_name}' not found"
        )
    
    mock = mock_engine.mocks[tool_name]
    
    # Toggle: if currently has failure mode "disabled", remove it; otherwise set it
    if mock.failure_mode and mock.failure_mode.get("error_type") == "disabled":
        mock.failure_mode = None  # Enable the mock
    else:
        mock.inject_failure(error_type="disabled", error_message="Mock is disabled")
    
    return _tool_mock_to_response(tool_name, mock)


@router.delete("/{tool_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mock(
    tool_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a mock"""
    if tool_name not in mock_engine.mocks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mock '{tool_name}' not found"
        )
    
    del mock_engine.mocks[tool_name]
    return None


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_all_mocks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset all mocks and call history"""
    mock_engine.reset_all()
    return None


@router.post("/{tool_name}/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_mock(
    tool_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset a specific mock"""
    if tool_name not in mock_engine.mocks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mock '{tool_name}' not found"
        )
    
    mock_engine.mocks[tool_name].reset()
    return None

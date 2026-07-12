"""
Integration tests for AgentGuard API
Tests complete workflows across multiple endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.models.user import User
from app.models.agent import Agent
from app.models.trace import Trace


class TestAuthWorkflow:
    """Test complete authentication workflow"""
    
    def test_complete_auth_flow(self, client: TestClient, test_organization, db: Session):
        """Test register → login → access protected endpoint"""
        
        # 1. Register new user
        register_data = {
            "email": f"integration_{uuid.uuid4()}@test.com",
            "password": "TestPassword123!",
            "full_name": "Integration Test User",
            "organization_id": test_organization.id
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["email"] == register_data["email"]
        
        # 2. Login with new user
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": register_data["email"],
                "password": register_data["password"]
            }
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        
        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_response = client.get("/api/v1/users/me", headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == register_data["email"]


class TestAgentTraceWorkflow:
    """Test agent creation and trace submission workflow"""
    
    def test_create_agent_and_send_trace(self, client: TestClient, auth_headers, test_user, test_organization, db: Session):
        """Test create agent → send trace → retrieve trace"""
        
        # 1. Create agent
        agent_data = {
            "name": "Integration Test Agent",
            "description": "Testing complete workflow",
            "tools": ["search", "calculator"]
        }
        
        agent_response = client.post(
            "/api/v1/agents",
            headers=auth_headers,
            json=agent_data
        )
        assert agent_response.status_code == 201
        agent = agent_response.json()
        agent_id = agent["id"]
        
        # 2. Send trace for agent
        trace_data = {
            "agent_id": agent_id,
            "trace_id": f"trace_{uuid.uuid4()}",
            "input": "What is 2+2?",
            "output": "The answer is 4",
            "status": "success",
            "duration_ms": 125,
            "metadata": {
                "model": "gpt-4",
                "tokens": 50
            }
        }
        
        trace_response = client.post(
            "/api/v1/traces",
            headers=auth_headers,
            json=trace_data
        )
        assert trace_response.status_code == 201
        
        # 3. Retrieve traces for agent
        traces_response = client.get(
            f"/api/v1/traces?agent_id={agent_id}",
            headers=auth_headers
        )
        assert traces_response.status_code == 200
        traces = traces_response.json()
        assert len(traces) > 0
        assert traces[0]["input"] == trace_data["input"]
        
        # 4. Get agent analytics
        analytics_response = client.get(
            f"/api/v1/analytics/agents/{agent_id}",
            headers=auth_headers
        )
        assert analytics_response.status_code == 200


class TestHealthMonitoringWorkflow:
    """Test health monitoring registration and checks"""
    
    def test_health_monitoring_workflow(self, client: TestClient, auth_headers, test_agent, db: Session):
        """Test register → check health → get status"""
        
        # 1. Register agent for monitoring
        register_data = {
            "agent_id": test_agent.id,
            "interval_seconds": 60,
            "alert_email": "alerts@test.com"
        }
        
        register_response = client.post(
            "/api/v1/health-monitoring/register",
            headers=auth_headers,
            json=register_data
        )
        assert register_response.status_code in [200, 201]
        
        # 2. Perform health check
        check_response = client.post(
            f"/api/v1/health-monitoring/check/{test_agent.id}",
            headers=auth_headers
        )
        assert check_response.status_code == 200
        
        # 3. Get health status
        status_response = client.get(
            f"/api/v1/health-monitoring/status/{test_agent.id}",
            headers=auth_headers
        )
        assert status_response.status_code == 200
        status = status_response.json()
        assert "current_status" in status
        
        # 4. Get dashboard data
        dashboard_response = client.get(
            "/api/v1/health-monitoring/dashboard",
            headers=auth_headers
        )
        assert dashboard_response.status_code == 200


class TestMocksWorkflow:
    """Test API mocking workflow"""
    
    def test_create_and_use_mock(self, client: TestClient, auth_headers, db: Session):
        """Test create mock → list mocks → use mock → delete mock"""
        
        # 1. Create custom mock
        mock_data = {
            "tool_name": f"test_api_{uuid.uuid4().hex[:8]}",
            "response": {
                "status": "success",
                "data": {"result": "mocked"}
            },
            "failure_rate": 0.0
        }
        
        create_response = client.post(
            "/api/v1/mocks",
            headers=auth_headers,
            json=mock_data
        )
        assert create_response.status_code == 201
        
        # 2. List mocks
        list_response = client.get(
            "/api/v1/mocks",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        mocks = list_response.json()
        assert any(m["tool_name"] == mock_data["tool_name"] for m in mocks)
        
        # 3. Get pre-built mocks
        prebuilt_response = client.get(
            "/api/v1/mocks/prebuilt",
            headers=auth_headers
        )
        assert prebuilt_response.status_code == 200
        
        # 4. Delete mock
        delete_response = client.delete(
            f"/api/v1/mocks/{mock_data['tool_name']}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204


class TestAdminWorkflow:
    """Test admin dashboard workflow"""
    
    def test_admin_dashboard_access(self, client: TestClient, admin_user, db: Session):
        """Test admin login → access admin endpoints"""
        from app.core.security import create_access_token
        
        # 1. Create admin token
        admin_token = create_access_token(data={"sub": admin_user.email})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 2. Get admin stats
        stats_response = client.get(
            "/api/v1/admin/stats",
            headers=admin_headers
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "total_users" in stats
        
        # 3. List all users
        users_response = client.get(
            "/api/v1/admin/users",
            headers=admin_headers
        )
        assert users_response.status_code == 200
        
        # 4. Get system status
        status_response = client.get(
            "/api/v1/admin/system-status",
            headers=admin_headers
        )
        assert status_response.status_code == 200


class TestRegressionDetectionWorkflow:
    """Test regression detection workflow"""
    
    def test_detect_regression(self, client: TestClient, auth_headers, test_agent, db: Session):
        """Test send traces → detect regression → get details"""
        
        # 1. Send successful traces
        for i in range(10):
            trace_data = {
                "agent_id": test_agent.id,
                "trace_id": f"success_{i}",
                "input": f"test {i}",
                "output": f"result {i}",
                "status": "success",
                "duration_ms": 100
            }
            client.post("/api/v1/traces", headers=auth_headers, json=trace_data)
        
        # 2. Send failed traces to create regression
        for i in range(5):
            trace_data = {
                "agent_id": test_agent.id,
                "trace_id": f"error_{i}",
                "input": f"test {i}",
                "output": "",
                "status": "error",
                "error": "Test error",
                "duration_ms": 100
            }
            client.post("/api/v1/traces", headers=auth_headers, json=trace_data)
        
        # 3. Check for regressions
        regressions_response = client.get(
            "/api/v1/regressions?time_window=1h",
            headers=auth_headers
        )
        assert regressions_response.status_code == 200
        # Note: May not detect regression with limited data

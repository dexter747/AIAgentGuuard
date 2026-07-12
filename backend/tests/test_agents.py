"""
Unit tests for agent management endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAgents:
    """Test agent management endpoints."""
    
    def test_create_agent(self, client: TestClient, auth_headers, test_organization):
        """Test creating a new agent."""
        response = client.post(
            "/api/v1/agents",
            headers=auth_headers,
            json={
                "name": "New Agent",
                "description": "Test agent description",
                "tools": ["web_search", "calculator"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Agent"
        assert data["description"] == "Test agent description"
        assert data["status"] == "active"
        assert "id" in data
    
    def test_create_agent_invalid_name(self, client: TestClient, auth_headers):
        """Test creating agent with invalid name (XSS attempt)."""
        response = client.post(
            "/api/v1/agents",
            headers=auth_headers,
            json={
                "name": "<script>alert('xss')</script>",
                "description": "Test"
            }
        )
        
        # Should either reject or sanitize
        assert response.status_code in [400, 422, 201]
        if response.status_code == 201:
            # If created, name should be sanitized
            data = response.json()
            assert "<script>" not in data["name"]
    
    def test_list_agents(self, client: TestClient, auth_headers, test_agent):
        """Test listing agents."""
        response = client.get("/api/v1/agents", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(agent["id"] == test_agent.id for agent in data)
    
    def test_get_agent(self, client: TestClient, auth_headers, test_agent):
        """Test getting specific agent."""
        response = client.get(f"/api/v1/agents/{test_agent.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_agent.id
        assert data["name"] == test_agent.name
    
    def test_get_nonexistent_agent(self, client: TestClient, auth_headers):
        """Test getting non-existent agent."""
        response = client.get("/api/v1/agents/nonexistent-id", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_agent(self, client: TestClient, auth_headers, test_agent):
        """Test updating agent."""
        response = client.put(
            f"/api/v1/agents/{test_agent.id}",
            headers=auth_headers,
            json={
                "name": "Updated Agent Name",
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Agent Name"
        assert data["description"] == "Updated description"
    
    def test_update_agent_unauthorized(self, client: TestClient, test_agent):
        """Test updating agent without authentication."""
        response = client.put(
            f"/api/v1/agents/{test_agent.id}",
            json={"name": "Hacked Name"}
        )
        
        assert response.status_code == 401
    
    def test_delete_agent(self, client: TestClient, auth_headers, test_agent):
        """Test deleting agent."""
        response = client.delete(f"/api/v1/agents/{test_agent.id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify agent is deleted
        response = client.get(f"/api/v1/agents/{test_agent.id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_agent_isolation_between_orgs(self, client: TestClient, auth_headers, test_agent, db: Session):
        """Test that agents are isolated between organizations."""
        from app.models.user import Organization
        from app.models.user import User
        from app.core.security import get_password_hash, create_access_token
        import uuid
        
        # Create another organization and user
        other_org = Organization(id=str(uuid.uuid4()), name="Other Org")
        db.add(other_org)
        db.commit()
        
        other_user = User(
            id=str(uuid.uuid4()),
            email="other@example.com",
            hashed_password=get_password_hash("password"),
            organization_id=other_org.id,
            is_active=True,
            is_verified=True
        )
        db.add(other_user)
        db.commit()
        
        other_token = create_access_token(data={"sub": other_user.email})
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Try to access test_agent from other org
        response = client.get(f"/api/v1/agents/{test_agent.id}", headers=other_headers)
        
        # Should not be able to see it
        assert response.status_code == 404

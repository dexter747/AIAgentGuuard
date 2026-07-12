"""
Seed database with sample data for development
"""
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import json

from app.core.database import SessionLocal
from app.models.user import User, Organization, UserRole, SubscriptionPlan
from app.models.agent import Agent
from app.models.trace import Trace
from app.models.test import Test, TestRun

def create_sample_org_and_user(db: Session):
    """Create a sample organization and user"""
    # Check if already exists
    existing_org = db.query(Organization).filter(Organization.name == "Demo Corp").first()
    if existing_org:
        print("Sample data already exists, skipping...")
        return existing_org, db.query(User).filter(User.org_id == existing_org.id).first()
    
    # Create organization
    org = Organization(
        name="Demo Corp",
        plan=SubscriptionPlan.PRO
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Create user
    user = User(
        email="demo@democorp.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS/Z8iMqi",  # "password123"
        org_id=org.id,
        role=UserRole.ADMIN,
        api_key="ag_live_demo_key_1234567890abcdef"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✅ Created organization: {org.name} (ID: {org.id})")
    print(f"✅ Created user: {user.email}")
    print(f"✅ API Key: {user.api_key}")
    
    return org, user


def create_sample_agents(db: Session, org_id: int):
    """Create sample agents"""
    agents_data = [
        {
            "name": "Router Agent",
            "endpoint_url": "https://api.example.com/router",
            "health_check_interval": 300
        },
        {
            "name": "Weather Agent",
            "endpoint_url": "https://api.example.com/weather",
            "health_check_interval": 600
        },
        {
            "name": "Stock Agent",
            "endpoint_url": "https://api.example.com/stock",
            "health_check_interval": 600
        },
        {
            "name": "Formatter Agent",
            "endpoint_url": "https://api.example.com/formatter",
            "health_check_interval": 600
        }
    ]
    
    created_agents = []
    for agent_data in agents_data:
        existing = db.query(Agent).filter(
            Agent.org_id == org_id,
            Agent.name == agent_data["name"]
        ).first()
        
        if not existing:
            agent = Agent(org_id=org_id, **agent_data)
            db.add(agent)
            db.commit()
            db.refresh(agent)
            created_agents.append(agent)
            print(f"✅ Created agent: {agent.name}")
        else:
            created_agents.append(existing)
    
    return created_agents


def create_sample_traces(db: Session, agents: list, org_id: int):
    """Create realistic trace data"""
    
    trace_scenarios = [
        {
            "agent_flow": ["Router Agent", "Weather Agent", "Formatter Agent"],
            "query": "What's the weather in Tokyo?",
            "status": "success",
            "steps": [
                {
                    "agent": "Router Agent",
                    "action": "classify_intent",
                    "input": {"query": "What's the weather in Tokyo?"},
                    "output": {"intent": "weather", "location": "Tokyo"},
                    "duration": 0.3,
                    "tokens": {"prompt": 45, "completion": 12},
                    "cost": 0.0001
                },
                {
                    "agent": "Weather Agent",
                    "action": "fetch_weather",
                    "input": {"location": "Tokyo"},
                    "output": {"temperature": 18, "condition": "Cloudy", "humidity": 65},
                    "duration": 1.2,
                    "tokens": {"prompt": 78, "completion": 34},
                    "cost": 0.0032
                },
                {
                    "agent": "Formatter Agent",
                    "action": "format_response",
                    "input": {"temperature": 18, "condition": "Cloudy"},
                    "output": {"response": "The weather in Tokyo is 18°C and cloudy with 65% humidity."},
                    "duration": 0.2,
                    "tokens": {"prompt": 56, "completion": 23},
                    "cost": 0.0001
                }
            ],
            "total_duration": 1.7
        },
        {
            "agent_flow": ["Router Agent", "Stock Agent", "Formatter Agent"],
            "query": "What's the price of AAPL stock?",
            "status": "success",
            "steps": [
                {
                    "agent": "Router Agent",
                    "action": "classify_intent",
                    "input": {"query": "What's the price of AAPL stock?"},
                    "output": {"intent": "stock", "symbol": "AAPL"},
                    "duration": 0.25,
                    "tokens": {"prompt": 48, "completion": 15},
                    "cost": 0.0001
                },
                {
                    "agent": "Stock Agent",
                    "action": "fetch_stock_price",
                    "input": {"symbol": "AAPL"},
                    "output": {"price": 178.42, "change": "+2.34", "change_percent": "+1.33%"},
                    "duration": 0.9,
                    "tokens": {"prompt": 92, "completion": 45},
                    "cost": 0.0028
                },
                {
                    "agent": "Formatter Agent",
                    "action": "format_response",
                    "input": {"symbol": "AAPL", "price": 178.42, "change": "+2.34"},
                    "output": {"response": "AAPL is currently trading at $178.42, up $2.34 (+1.33%) today."},
                    "duration": 0.18,
                    "tokens": {"prompt": 61, "completion": 28},
                    "cost": 0.0001
                }
            ],
            "total_duration": 1.33
        },
        {
            "agent_flow": ["Router Agent", "Weather Agent"],
            "query": "Weather in InvalidCity123",
            "status": "error",
            "steps": [
                {
                    "agent": "Router Agent",
                    "action": "classify_intent",
                    "input": {"query": "Weather in InvalidCity123"},
                    "output": {"intent": "weather", "location": "InvalidCity123"},
                    "duration": 0.28,
                    "tokens": {"prompt": 47, "completion": 14},
                    "cost": 0.0001
                },
                {
                    "agent": "Weather Agent",
                    "action": "fetch_weather",
                    "input": {"location": "InvalidCity123"},
                    "output": {"error": "Location not found"},
                    "duration": 0.8,
                    "tokens": {"prompt": 68, "completion": 18},
                    "cost": 0.0021
                }
            ],
            "total_duration": 1.08,
            "error": "Location not found: InvalidCity123"
        }
    ]
    
    agent_map = {agent.name: agent for agent in agents}
    
    # Create 50 traces with variation
    for i in range(50):
        scenario = random.choice(trace_scenarios)
        
        # Get the first agent in the flow
        first_agent_name = scenario["agent_flow"][0]
        agent = agent_map.get(first_agent_name)
        
        if not agent:
            continue
        
        # Calculate totals
        total_tokens = sum(
            step["tokens"]["prompt"] + step["tokens"]["completion"] 
            for step in scenario["steps"]
        )
        total_cost = sum(step["cost"] for step in scenario["steps"])
        
        # Create trace with random timestamp in last 7 days
        created_at = datetime.utcnow() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        duration_ms = int((scenario["total_duration"] + random.uniform(-0.2, 0.3)) * 1000)
        
        trace = Trace(
            agent_id=agent.id,
            trace_data={
                "query": scenario["query"],
                "status": scenario["status"],
                "steps": scenario["steps"],
                "agent_flow": scenario["agent_flow"],
                "error": scenario.get("error")
            },
            start_time=created_at,
            end_time=created_at + timedelta(milliseconds=duration_ms),
            status=scenario["status"],
            total_duration_ms=duration_ms,
            token_count=total_tokens + random.randint(-10, 10),
            cost_usd=f"{total_cost:.6f}",
            created_at=created_at
        )
        db.add(trace)
    
    db.commit()
    print(f"✅ Created 50 sample traces")


def create_sample_tests(db: Session, agents: list, org_id: int):
    """Create sample tests"""
    
    for agent in agents[:2]:  # Create tests for first 2 agents
        test = Test(
            agent_id=agent.id,
            name=f"Integration test for {agent.name}",
            code=f'''
import pytest
from agent_system import {agent.name.replace(" ", "")}

def test_{agent.name.replace(" ", "_").lower()}_response():
    agent = {agent.name.replace(" ", "")}()
    result = agent.execute("test input")
    assert result is not None
    assert "error" not in result
            '''.strip()
        )
        db.add(test)
        db.commit()
        db.refresh(test)
        
        # Create a test run
        test_run = TestRun(
            test_id=test.id,
            status="passed",
            duration_ms=2400,
            logs="All assertions passed successfully"
        )
        db.add(test_run)
    
    db.commit()
    print(f"✅ Created sample tests and test runs")


def main():
    """Seed the database"""
    print("🌱 Seeding database...")
    
    db = SessionLocal()
    try:
        org, user = create_sample_org_and_user(db)
        agents = create_sample_agents(db, org.id)
        create_sample_traces(db, agents, org.id)
        create_sample_tests(db, agents, org.id)
        
        print("\n" + "="*60)
        print("✨ Database seeded successfully!")
        print("="*60)
        if user:
            print(f"\n📧 Login: {user.email}")
            print(f"🔑 API Key: {user.api_key}")
        if org:
            print(f"📊 Organization: {org.name} ({org.plan.value} plan)")
        print("\n🚀 You can now test the API endpoints!\n")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

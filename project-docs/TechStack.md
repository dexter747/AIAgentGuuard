# Technology Stack Summary
## AgentGuard Simplified Architecture

**Last Updated**: January 23, 2026

---

## Tech Stack Decision

### ✅ What We're Using

| Component | Technology | Why |
|-----------|-----------|-----|
| **Backend API** | FastAPI (Python 3.11+) | Fast, simple, great docs |
| **Database ORM** | SQLAlchemy | Industry standard, flexible |
| **Database** | PostgreSQL 14+ | Reliable, handles JSON well |
| **Cache** | Redis 7 | Fast sessions, rate limiting |
| **Frontend** | Next.js (React 18) | SEO, server rendering, great DX |
| **Payments** | Dodo Payments | Easy integration, handles compliance |
| **Deployment** | Vercel + Railway/Render | Simple, auto-scaling |
| **Email** | SendGrid | Reliable email delivery |
| **Containerization** | Docker (optional) | Use only if needed |

### ❌ What We're NOT Using (Avoiding Over-Engineering)

- ~~Kubernetes~~ → Use managed hosting instead (Railway, Render)
- ~~Microservices~~ → Monolithic FastAPI app is fine for now
- ~~RabbitMQ/Kafka~~ → Python async + PostgreSQL queue is enough
- ~~S3/Cloud Storage~~ → PostgreSQL JSONB can store traces
- ~~Service Mesh~~ → Not needed at our scale
- ~~ElasticSearch~~ → PostgreSQL full-text search works fine
- ~~GraphQL~~ → REST API is simpler

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Users (Browser/SDK)              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      Next.js Frontend (Vercel)          │
│  - User Dashboard                        │
│  - Admin Portal                          │
│  - Authentication UI                     │
└─────────────────┬───────────────────────┘
                  │ REST API
                  ▼
┌─────────────────────────────────────────┐
│    FastAPI Backend (Railway/Render)     │
│  ┌─────────────────────────────────┐   │
│  │ Core Modules:                   │   │
│  │  • Trace Ingestion              │   │
│  │  • Test Generation              │   │
│  │  • Test Execution               │   │
│  │  • Health Monitoring            │   │
│  │  • Mock Engine                  │   │
│  │  • User Management              │   │
│  │  • Billing Integration          │   │
│  └─────────────────────────────────┘   │
└──────┬──────────────┬─────────────┬────┘
       │              │             │
       ▼              ▼             ▼
┌─────────────┐ ┌──────────┐ ┌──────────────┐
│ PostgreSQL  │ │  Redis   │ │Dodo Payments │
│  (Managed)  │ │(Managed) │ │    (API)     │
└─────────────┘ └──────────┘ └──────────────┘
```

---

## File Structure

```
agentguard/
├── frontend/                 # Next.js app
│   ├── app/                 # App router
│   │   ├── dashboard/       # User dashboard
│   │   ├── admin/           # Admin portal
│   │   ├── tests/           # Test management
│   │   └── monitoring/      # Health monitoring
│   ├── components/          # React components
│   └── public/              # Static assets
│
├── backend/                 # FastAPI app
│   ├── main.py             # FastAPI entry point
│   ├── models.py           # SQLAlchemy models
│   ├── api/                # API routes
│   │   ├── traces.py
│   │   ├── tests.py
│   │   ├── health.py
│   │   ├── users.py
│   │   └── billing.py
│   ├── services/           # Business logic
│   │   ├── trace_parser.py
│   │   ├── test_generator.py
│   │   ├── mock_engine.py
│   │   └── health_monitor.py
│   ├── database.py         # SQLAlchemy setup
│   └── config.py           # Configuration
│
├── sdk/                    # Python SDK
│   └── agentguard/
│       ├── __init__.py
│       ├── client.py
│       └── tracing.py
│
├── docker-compose.yml      # Optional: local dev
└── README.md
```

---

## Database Schema (Simplified)

### Core Tables

**organizations**
- id, name, plan, stripe_customer_id, created_at

**users**
- id, org_id, email, password_hash, role, created_at

**agents**
- id, org_id, name, endpoint_url, health_check_interval, created_at

**traces** (stores execution history)
- id, agent_id, trace_data (JSONB), start_time, end_time, status, cost_usd

**tests** (generated test cases)
- id, agent_id, name, code (TEXT), source_trace_id, is_active

**test_runs** (test execution results)
- id, test_id, status, duration_ms, error_message, created_at

**health_checks** (monitoring data)
- id, agent_id, status, response_time_ms, checked_at

**subscriptions** (billing)
- id, org_id, plan, status, current_period_end, created_at

---

## Deployment Guide

### Option 1: Cloud Services (Recommended for MVP)

**Frontend (Vercel)**:
```bash
# Connect GitHub repo
# Vercel auto-deploys on push
# Environment: production
```

**Backend (Railway/Render)**:
```bash
# Connect GitHub repo
# Set environment variables:
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
DODO_API_KEY=...
SECRET_KEY=...
```

**Database (Railway/Supabase)**:
- Provision PostgreSQL 14+
- Auto backups enabled
- Connection string → backend env

**Cache (Upstash/Redis Cloud)**:
- Provision Redis 7
- Connection string → backend env

### Option 2: Docker (Optional)

**When to use**:
- Multi-developer team needs consistency
- Self-hosted deployment
- Complex local setup

**docker-compose.yml**:
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/agentguard
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=agentguard
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**Run**:
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Option 3: Local Development (No Docker)

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL and Redis locally
# Or use cloud services for dev too

uvicorn main:app --reload
# API: http://localhost:8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
# UI: http://localhost:3000
```

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentguard

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Dodo Payments
DODO_API_KEY=your-dodo-api-key
DODO_WEBHOOK_SECRET=your-webhook-secret

# Email
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@agentguard.io

# App Settings
ENVIRONMENT=development  # or production
DEBUG=True  # False in production
CORS_ORIGINS=http://localhost:3000,https://agentguard.io
```

### Frontend (.env.local)

```bash
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000  # or production URL

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_ADMIN_PORTAL=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

---

## Development Workflow

### 1. Local Setup
```bash
# Clone repo
git clone https://github.com/yourorg/agentguard.git
cd agentguard

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head  # Run migrations
uvicorn main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### 2. Database Migrations
```bash
# Create migration
alembic revision -m "add new table"

# Edit migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 3. Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### 4. Deployment
```bash
# Push to main branch
git push origin main

# Vercel auto-deploys frontend
# Railway auto-deploys backend

# Or manual deploy
vercel --prod  # frontend
railway up     # backend
```

---

## Scaling Strategy

### Phase 1: 0-1,000 users
- ✅ Single FastAPI instance
- ✅ Managed PostgreSQL
- ✅ Managed Redis
- **Cost**: ~$50-100/month

### Phase 2: 1K-10K users
- Add: Multiple FastAPI instances (horizontal scaling)
- Add: Load balancer (Railway/Render handles this)
- Optimize: Database queries, add indexes
- **Cost**: ~$200-500/month

### Phase 3: 10K+ users
- Add: PostgreSQL read replicas
- Add: Redis cluster
- Add: CDN for static assets
- Consider: Separate worker processes for background jobs
- **Cost**: ~$1000+/month

---

## Security Checklist

- [x] HTTPS everywhere (TLS 1.3)
- [x] Password hashing (bcrypt)
- [x] JWT authentication
- [x] Rate limiting (Redis-based)
- [x] Input validation (Pydantic)
- [x] SQL injection protection (SQLAlchemy ORM)
- [x] CORS configuration
- [x] Environment variables for secrets
- [ ] SOC 2 compliance (Enterprise tier goal)
- [ ] Two-factor authentication (future)
- [ ] Audit logging (future)

---

## Monitoring & Logging

### Application Logging
```python
# backend/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Error Tracking
- Start simple: Python logging
- Later: Sentry (when budget allows)

### Performance Monitoring
- Railway/Render built-in metrics
- PostgreSQL slow query log
- Custom endpoints: `/health`, `/metrics`

---

## Admin Portal Features

### User Management
- View all users in organization
- Invite users (send email with signup link)
- Change user roles (Admin, Member, Viewer)
- Deactivate/remove users

### Billing Management
- View current plan and usage
- Upgrade/downgrade via Dodo Payments
- Download invoices
- Update payment method
- View usage breakdown

### Organization Settings
- Update company name
- Configure default settings
- Set data retention policy
- Manage API keys

### Security
- View audit log
- Configure IP whitelist (Enterprise)
- Enable 2FA (future)
- Rotate secrets

---

## Common Pitfalls to Avoid

❌ **Don't**: Use Docker in production without understanding it  
✅ **Do**: Use managed services (Vercel, Railway) until you need containers

❌ **Don't**: Build microservices from day 1  
✅ **Do**: Start with monolith, split later if needed

❌ **Don't**: Optimize prematurely  
✅ **Do**: Build features, optimize when users complain

❌ **Don't**: Store secrets in code  
✅ **Do**: Use environment variables

❌ **Don't**: Skip backups  
✅ **Do**: Enable automated database backups

---

## Quick Start Commands

```bash
# Development
npm run dev          # Frontend
uvicorn main:app --reload  # Backend

# Testing
pytest               # Backend tests
npm test            # Frontend tests

# Database
alembic upgrade head     # Apply migrations
alembic revision -m ""   # Create migration

# Deployment
git push origin main     # Auto-deploys
vercel --prod           # Manual frontend deploy
railway up              # Manual backend deploy

# Maintenance
docker-compose down     # Stop all services
docker-compose logs -f  # View logs
```

---

## Need Help?

- **Documentation**: Check the README.md in each folder
- **Issues**: GitHub Issues for bug reports
- **Questions**: Team Slack channel
- **Architecture**: Review this doc and Architecture.md

---

**Remember**: Start simple, ship fast, optimize later! 🚀

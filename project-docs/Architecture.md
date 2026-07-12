# AgentGuard System Architecture
## Technical Architecture Document

**Version**: 1.0  
**Date**: January 23, 2026  
**Status**: Draft

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Architecture Principles](#3-architecture-principles)
4. [Component Architecture](#4-component-architecture)
5. [Data Architecture](#5-data-architecture)
6. [Deployment Architecture](#6-deployment-architecture)
7. [Security Architecture](#7-security-architecture)
8. [Integration Architecture](#8-integration-architecture)
9. [Scalability & Performance](#9-scalability--performance)
10. [Disaster Recovery](#10-disaster-recovery)

---

## 1. Executive Summary

AgentGuard is a cloud-native, distributed system designed to provide comprehensive testing and monitoring capabilities for AI agents. The architecture follows microservices principles, leveraging containerization, message queues, and distributed caching to achieve high availability, scalability, and performance.

**Key Architectural Highlights**:
- Microservices architecture with independent scaling
- Event-driven communication for asynchronous operations
- Multi-region deployment for global low latency
- Polyglot persistence (PostgreSQL, Redis, S3)
- API-first design with comprehensive SDK support

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Layer                                 │
├─────────────────────────────────────────────────────────────────────┤
│  User Dashboard │  Admin Portal │  Python SDK  │  JavaScript SDK    │
│  (Next.js)      │  (Next.js)    │              │                    │
└────────┬────────────────┬─────────────┬─────────────────┬───────────┘
         │                │             │                 │
         └────────────────┴─────────────┴─────────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │   FastAPI Backend       │
                    │   - REST API            │
                    │   - Authentication      │
                    └───────────┬─────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Trace Module   │  │  Test Module    │  │ Health Module   │
│  - Ingestion    │  │  - Generation   │  │  - Monitoring   │
│  - Parsing      │  │  - Execution    │  │  - Alerting     │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  PostgreSQL     │  │  Redis Cache    │  │  Dodo Payments  │
│  (SQLAlchemy)   │  │  - Sessions     │  │  - Billing API  │
│  - All data     │  │  - Rate limit   │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **User Dashboard** | User interface for developers | Next.js, React |
| **Admin Portal** | Organization and billing management | Next.js, React |
| **FastAPI Backend** | REST API, business logic | Python 3.11+, FastAPI |
| **Trace Module** | Ingest and process traces | Python, SQLAlchemy |
| **Test Module** | Generate and execute tests | Python (pytest) |
| **Health Module** | Monitor agent endpoints | Python (async) |
| **Mock Engine** | Simulate API responses | Python |
| **PostgreSQL** | Persistent data storage | PostgreSQL 14+ |
| **Redis** | Caching and sessions | Redis 7+ |
| **Dodo Payments** | Subscription billing | Third-party API |

### 2.3 Communication Patterns

**Synchronous Communication**:
- REST API calls (FastAPI endpoints)
- HTTP requests between frontend and backend
- Database queries via SQLAlchemy ORM

**Asynchronous Communication**:
- Background jobs for test execution
- Scheduled health checks (async Python)
- Email/Slack notifications

**Data Flow**:
1. User interacts with Next.js frontend
2. Frontend makes REST API calls to FastAPI
3. FastAPI processes requests, queries PostgreSQL
4. Results cached in Redis when appropriate
5. Background jobs handle long-running tasks
6. Notifications sent via SendGrid/Slack APIs

---

## 3. Architecture Principles

### 3.1 Design Principles

**1. API-First Design**
- All functionality exposed via APIs
- Internal services communicate via APIs
- SDKs auto-generated from OpenAPI specs

**2. Loose Coupling**
- Services communicate via message queues
- No direct database access between services
- Event-driven architecture for independence

**3. High Cohesion**
- Each service has single responsibility
- Related functionality grouped together
- Clear service boundaries

**4. Resilience**
- Circuit breakers for external dependencies
- Graceful degradation on failures
- Retry mechanisms with exponential backoff

**5. Observability**
- Structured logging (JSON format)
- Distributed tracing (OpenTelemetry)
- Metrics collection (Prometheus)

### 3.2 Technology Choices

| Requirement | Technology | Rationale |
|-------------|-----------|-----------|
| **Backend API** | FastAPI (Python) | High performance, auto-docs, async support, simple |
| **ORM** | SQLAlchemy | Industry standard, flexible, migration support |
| **Frontend** | Next.js (React 18) | Server-side rendering, SEO, great DX |
| **Database** | PostgreSQL 14 | ACID compliance, JSONB support, reliable |
| **Cache** | Redis 7 | Fast, simple, session management |
| **Payments** | Dodo Payments | Easy integration, handles compliance |
| **Deployment** | Vercel (optional Docker) | Simple, auto-scaling, Next.js optimized |
| **Monitoring** | Built-in logging | Simple to start, upgrade later if needed |

---

## 4. Component Architecture

### 4.1 Trace Service

**Purpose**: Ingest, parse, and store agent execution traces

**Subcomponents**:

```
┌─────────────────────────────────────────────────────────┐
│                    Trace Service                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐   ┌─────────────────┐             │
│  │  Ingestion API  │   │  Parser Engine  │             │
│  │  - OTLP/gRPC    │──▶│  - Langfuse     │             │
│  │  - Langfuse     │   │  - OpenTelemetry│             │
│  │  - Webhooks     │   │  - Normalization│             │
│  └─────────────────┘   └────────┬────────┘             │
│                                  │                       │
│                         ┌────────▼────────┐             │
│                         │ Trace Validator │             │
│                         │ - Schema check  │             │
│                         │ - Sanitization  │             │
│                         └────────┬────────┘             │
│                                  │                       │
│  ┌─────────────────┐   ┌────────▼────────┐             │
│  │  Storage Layer  │◀──│  Trace Indexer  │             │
│  │  - PostgreSQL   │   │  - Search index │             │
│  │  - S3 (raw)     │   │  - Tags/metadata│             │
│  └─────────────────┘   └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Data Flow**:
1. Client sends trace via SDK
2. Ingestion API validates request (auth, format)
3. Parser normalizes trace to common format
4. Validator checks schema and sanitizes data
5. Indexer extracts metadata for search
6. Storage layer persists to PostgreSQL + S3

**Performance Targets**:
- Ingestion throughput: 10,000 traces/minute
- Parse latency: <100ms per trace
- Storage latency: <500ms end-to-end

**Scaling Strategy**:
- Horizontal scaling of ingestion API pods
- Partitioned PostgreSQL database (by customer_id)
- S3 for archival of raw traces (>30 days old)

### 4.2 Test Service

**Purpose**: Generate tests from traces and execute test suites

**Subcomponents**:

```
┌─────────────────────────────────────────────────────────┐
│                     Test Service                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐   ┌──────────────────┐           │
│  │  Test Generator  │   │ Pattern Detector │           │
│  │  - Trace→Code    │◀──│  - ML model      │           │
│  │  - pytest syntax │   │  - Clustering    │           │
│  │  - Assertions    │   │  - Deduplication │           │
│  └────────┬─────────┘   └──────────────────┘           │
│           │                                              │
│  ┌────────▼─────────┐   ┌──────────────────┐           │
│  │  Test Executor   │   │  Mock Injector   │           │
│  │  - pytest runner │◀──│  - Tool mocks    │           │
│  │  - Parallel runs │   │  - State mgmt    │           │
│  │  - Result collect│   │  - Failure inject│           │
│  └────────┬─────────┘   └──────────────────┘           │
│           │                                              │
│  ┌────────▼─────────┐   ┌──────────────────┐           │
│  │ Result Analyzer  │   │  Regression Det. │           │
│  │  - Pass/fail     │──▶│  - Baseline comp │           │
│  │  - Coverage      │   │  - Metric drift  │           │
│  │  - Screenshots   │   │  - Alert trigger │           │
│  └──────────────────┘   └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

**Test Generation Algorithm**:
1. Fetch trace from storage
2. Identify tool call sequence
3. Extract input/output pairs
4. Generate pytest function with:
   - Descriptive name based on trace summary
   - Mock setup for each tool call
   - Assertions on final output
   - Assertions on tool call count/order
5. Store test code in database
6. Mark test for execution

**Execution Workflow**:
1. Pull test from queue
2. Inject mocks into agent runtime
3. Execute test in isolated environment
4. Collect results (stdout, logs, metrics)
5. Compare against baseline
6. Publish results to analytics service

**Performance Targets**:
- Test generation: <5 seconds per trace
- Test execution: 100 concurrent tests
- Result processing: <1 second per test

### 4.3 Health Service

**Purpose**: Monitor agent availability and send alerts

**Subcomponents**:

```
┌─────────────────────────────────────────────────────────┐
│                    Health Service                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐   ┌──────────────────┐           │
│  │  Probe Scheduler │   │  Probe Workers   │           │
│  │  - Cron jobs     │──▶│  - HTTP client   │           │
│  │  - Distribution  │   │  - Multi-region  │           │
│  │  - Prioritization│   │  - Timeout mgmt  │           │
│  └──────────────────┘   └────────┬─────────┘           │
│                                   │                      │
│  ┌──────────────────┐   ┌────────▼─────────┐           │
│  │ Response Checker │   │  State Machine   │           │
│  │  - Schema valid  │◀──│  - Healthy       │           │
│  │  - Latency check │   │  - Degraded      │           │
│  │  - Dependency OK │   │  - Unhealthy     │           │
│  └────────┬─────────┘   └──────────────────┘           │
│           │                                              │
│  ┌────────▼─────────┐   ┌──────────────────┐           │
│  │  Alert Manager   │   │  Escalation Eng. │           │
│  │  - Deduplication │──▶│  - Threshold     │           │
│  │  - Throttling    │   │  - Multi-channel │           │
│  │  - Routing       │   │  - On-call lookup│           │
│  └──────────────────┘   └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

**Health Check State Machine**:

```
                    ┌──────────┐
         ┌──────────│ HEALTHY  │◀──────────┐
         │          └─────┬────┘           │
         │                │                 │
  3 successes      1 failure        3 successes
         │                │                 │
         │          ┌─────▼────┐           │
         └──────────│ DEGRADED │───────────┘
                    └─────┬────┘
                          │
                   2 failures
                          │
                    ┌─────▼────┐
                    │UNHEALTHY │
                    └──────────┘
```

**Alert Escalation Policy**:
- 1 failure: Log only (no alert)
- 2 failures within 10min: Email to team
- 3 failures within 15min: Email + Slack
- 5 failures within 30min: PagerDuty incident

**Performance Targets**:
- Probe frequency: Every 1-60 minutes (configurable)
- Probe timeout: 30 seconds default
- Alert delivery: <30 seconds from detection
- False positive rate: <0.1%

### 4.4 Mock Service

**Purpose**: Simulate external API responses during testing

**Subcomponents**:

```
┌─────────────────────────────────────────────────────────┐
│                     Mock Service                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐   ┌──────────────────┐           │
│  │  Request Matcher │   │  Mock Repository │           │
│  │  - URL pattern   │──▶│  - Response DB   │           │
│  │  - Method        │   │  - Templates     │           │
│  │  - Headers       │   │  - Fixtures      │           │
│  │  - Body match    │   └──────────────────┘           │
│  └────────┬─────────┘                                   │
│           │                                              │
│  ┌────────▼─────────┐   ┌──────────────────┐           │
│  │ Response Builder │   │  State Manager   │           │
│  │  - Template fill │◀──│  - Session store │           │
│  │  - Dynamic data  │   │  - CRUD tracking │           │
│  │  - Latency sim   │   │  - Reset logic   │           │
│  └────────┬─────────┘   └──────────────────┘           │
│           │                                              │
│  ┌────────▼─────────┐   ┌──────────────────┐           │
│  │ Failure Injector │   │  Tool Integra... │           │
│  │  - Error codes   │   │  - Stripe        │           │
│  │  - Timeouts      │   │  - SendGrid      │           │
│  │  - Chaos testing │   │  - Slack, etc.   │           │
│  └──────────────────┘   └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

**Mock Matching Priority**:
1. Exact URL + method + body match
2. URL + method + partial body match
3. URL pattern + method match
4. Default response for tool

**State Management**:
- Each test run gets isolated state
- State persists across agent turns within test
- State reset after test completion
- Support for stateful APIs (create → read → update)

**Supported Mock Types**:
- **Static mocks**: Fixed responses
- **Dynamic mocks**: Template-based responses
- **Stateful mocks**: Track entity lifecycle
- **Probabilistic mocks**: Random responses from set
- **Failure mocks**: Inject errors/timeouts

---

## 5. Data Architecture

### 5.1 Database Schema

**PostgreSQL Tables**:

```sql
-- Organizations & Users
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50), -- free, pro, team, enterprise
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    org_id UUID REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50), -- admin, member, viewer
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agents
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    org_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    endpoint_url VARCHAR(500),
    health_check_interval INTEGER DEFAULT 300, -- seconds
    created_at TIMESTAMP DEFAULT NOW()
);

-- Traces
CREATE TABLE traces (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    span_id VARCHAR(100),
    parent_span_id VARCHAR(100),
    trace_data JSONB NOT NULL, -- full trace payload
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50), -- success, error, timeout
    token_count INTEGER,
    cost_usd DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_traces_agent_time ON traces(agent_id, start_time DESC);
CREATE INDEX idx_traces_jsonb ON traces USING GIN(trace_data);

-- Tests
CREATE TABLE tests (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    name VARCHAR(255) NOT NULL,
    code TEXT NOT NULL, -- pytest code
    source_trace_id UUID REFERENCES traces(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Test Runs
CREATE TABLE test_runs (
    id UUID PRIMARY KEY,
    test_id UUID REFERENCES tests(id),
    status VARCHAR(50), -- pending, running, passed, failed
    duration_ms INTEGER,
    error_message TEXT,
    logs TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Health Checks
CREATE TABLE health_checks (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    probe_region VARCHAR(50), -- us-east-1, eu-west-1
    status VARCHAR(50), -- healthy, degraded, unhealthy
    response_time_ms INTEGER,
    response_body JSONB,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_health_agent_time ON health_checks(agent_id, checked_at DESC);

-- Mocks
CREATE TABLE mocks (
    id UUID PRIMARY KEY,
    org_id UUID REFERENCES organizations(id),
    tool_name VARCHAR(100), -- stripe, sendgrid, etc.
    request_pattern JSONB, -- matching criteria
    response_template JSONB, -- response structure
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    severity VARCHAR(50), -- info, warning, critical
    title VARCHAR(255),
    message TEXT,
    channels JSONB, -- ["email", "slack"]
    sent_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP
);
```

### 5.2 Redis Cache Structure

```
# Session management
session:{session_id} → {user_id, org_id, expires_at}
TTL: 24 hours

# Rate limiting
ratelimit:{api_key}:{minute} → request_count
TTL: 60 seconds

# Health check state
health:state:{agent_id} → {status, consecutive_failures, last_check}
TTL: 7 days

# Test run queue
queue:test_runs → List of test_ids to execute

# Temporary cache
cache:{key} → value
TTL: Varies (1 hour default)
```

### 5.3 Data Retention

**PostgreSQL**:
- Active data: Unlimited (within plan limits)
- Soft delete: 30 days before permanent deletion
- Audit logs: 1 year for Enterprise, 90 days for others

**Redis**:
- Sessions: 24 hours
- Rate limits: 1 minute
- Temporary cache: 1 hour default

**Backups**:
- PostgreSQL: Daily automated backups (7-day retention)
- Point-in-time recovery available for Enterprise tier

---

## 6. Deployment Architecture

### 6.1 Simple Cloud Deployment

**Recommended Stack:**
- **Frontend**: Vercel (Next.js optimized hosting)
- **Backend**: Railway.app, Render, or AWS EC2
- **Database**: Managed PostgreSQL (Railway, Supabase, AWS RDS)
- **Cache**: Managed Redis (Upstash, Redis Cloud)
- **Containerization**: Optional Docker for consistency

**Architecture:**
```
Users
  ↓
Vercel (Next.js App)
  ↓
FastAPI Backend (Railway/Render)
  ↓
  ├──> PostgreSQL (Managed)
  ├──> Redis (Managed)
  └──> Dodo Payments API
```

### 6.2 Docker Deployment (Optional)

**When to use Docker:**
- Consistent dev/prod environments
- Multi-developer teams
- Self-hosted deployments

**docker-compose.yml structure:**
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:14
    volumes:
      - pg_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
```

**Note**: Docker is NOT required for initial development. Start simple with local Python venv and node_modules.

### 6.3 Scaling Strategy

**Phase 1 (0-1000 users)**: Single backend server, managed DB  
**Phase 2 (1K-10K users)**: Multiple backend instances behind load balancer  
**Phase 3 (10K+ users)**: Database read replicas, Redis cluster

---

## 7. Security Architecture

### 7.1 Authentication Flow

```
User → Auth0 → JWT Token → API Gateway → Verify Token → Allow Request
```

**Supported Methods**:
- Email/Password (bcrypt hashing)
- OAuth 2.0 (Google, GitHub)
- SAML 2.0 (Enterprise SSO)
- API Keys (service accounts)

### 7.2 Authorization Model

**Role-Based Access Control (RBAC)**:

| Role | Permissions |
|------|-------------|
| **Viewer** | Read tests, view dashboards |
| **Member** | Viewer + Create tests, run tests |
| **Admin** | Member + Manage users, configure agents |
| **Owner** | Admin + Billing, delete organization |

**Resource-Level Permissions**:
- Organization-scoped (can't access other orgs)
- API keys scoped to specific agents
- Fine-grained permissions via policies

### 7.3 Data Encryption

**In Transit**:
- TLS 1.3 for all HTTP traffic
- Certificate pinning for SDKs
- VPN for admin access

**At Rest**:
- PostgreSQL: Transparent Data Encryption (TDE)
- S3: Server-side encryption (SSE-S3)
- Redis: Encryption at rest (if supported by provider)

**Secrets Management**:
- HashiCorp Vault for production secrets
- AWS Secrets Manager (alternative)
- No secrets in code or environment variables

---

## 8. Integration Architecture

### 8.1 SDK Architecture

**Python SDK**:
```python
agentguard/
├── __init__.py
├── client.py          # Main AgentGuard client
├── tracing.py         # Trace instrumentation
├── mocking.py         # Mock context manager
├── health.py          # Health check helpers
├── models/            # Pydantic models
│   ├── trace.py
│   ├── test.py
│   └── health.py
└── utils/
    ├── auth.py
    └── http.py
```

**JavaScript SDK**:
```typescript
@agentguard/sdk/
├── index.ts
├── client.ts
├── tracing.ts
├── mocking.ts
├── health.ts
├── models/
│   ├── trace.ts
│   ├── test.ts
│   └── health.ts
└── utils/
    ├── auth.ts
    └── http.ts
```

### 8.2 External Integrations

**Tracing Sources**:
- Langfuse: Webhook receiver
- OpenTelemetry: OTLP/gRPC endpoint
- LangSmith: API polling (future)

**Notification Targets**:
- Email: SendGrid API (primary), AWS SES (fallback)
- Slack: OAuth 2.0 bot integration
- PagerDuty: Events API v2
- Microsoft Teams: Incoming webhook

**CI/CD Platforms**:
- GitHub Actions: Marketplace action
- GitLab CI: Docker image
- Jenkins: Plugin
- CircleCI: Orb

---

## 9. Scalability & Performance

### 9.1 Auto-Scaling Configuration

**Horizontal Pod Autoscaler (HPA)**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: trace-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: trace-service
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 9.2 Performance Optimization

**Caching Strategy**:
- Redis for hot data (< 5 min old)
- CDN for static assets (CloudFlare)
- Browser caching (365 days for immutable assets)

**Database Optimization**:
- Connection pooling (pgBouncer)
- Read replicas for analytics queries
- Partitioning on `created_at` for large tables
- JSONB indexes for trace queries

**API Optimization**:
- Pagination (default 50 items/page)
- Field filtering (GraphQL-style)
- Response compression (gzip, brotli)
- HTTP/2 multiplexing

---

## 10. Disaster Recovery

### 10.1 Backup Strategy

**PostgreSQL**:
- Continuous WAL archiving to S3
- Daily full backups (retained 30 days)
- Point-in-time recovery capability

**Redis**:
- RDB snapshots every 6 hours
- AOF (Append-Only File) for durability
- Replicate to backup instance

**S3**:
- Versioning enabled
- Cross-region replication
- Lifecycle policies for cost optimization

### 10.2 Recovery Procedures

**Database Failure**:
1. Detect via health checks (< 1 min)
2. Failover to replica (< 5 min)
3. Update DNS records
4. Monitor replication lag

**Region Failure**:
1. Route53 automatic failover (< 1 min)
2. Scale up secondary region capacity
3. Verify data consistency
4. Incident postmortem

**Recovery Time Objective (RTO)**: 15 minutes  
**Recovery Point Objective (RPO)**: 5 minutes

---

## Appendices

### A. Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React 18, TypeScript, TailwindCSS |
| **Backend** | Python 3.11+, FastAPI, Pydantic |
| **ORM** | SQLAlchemy |
| **Database** | PostgreSQL 14+ |
| **Cache** | Redis 7 |
| **Payments** | Dodo Payments API |
| **Deployment** | Vercel (frontend), Railway/Render (backend) |
| **Containerization** | Docker (optional) |
| **Email** | SendGrid |
| **Monitoring** | Python logging, error tracking |

### B. Why This Stack?

**Simplicity**: Fewer moving parts = easier to build and maintain  
**Cost-effective**: Managed services reduce ops overhead  
**Developer-friendly**: Popular technologies with great documentation  
**Scalable**: Can handle 10K+ users before needing optimization  
**No over-engineering**: Docker/Kubernetes only when actually needed

---

| Metric | Target | Actual (Load Test) |
|--------|--------|-------------------|
| API Response Time (p95) | <500ms | 380ms |
| Trace Ingestion Rate | 10K/min | 12.5K/min |
| Test Execution Throughput | 100 concurrent | 120 concurrent |
| Dashboard Load Time | <2s | 1.7s |
| Health Check Latency | <100ms | 65ms |

---

**Document Approval**

| Role | Name | Date |
|------|------|------|
| Principal Architect | | |
| VP Engineering | | |
| Security Lead | | |

---

**End of Architecture Document**

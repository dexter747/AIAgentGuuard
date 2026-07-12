# Pre-Beta Testing Checklist

## Critical Workflows to Test Before Beta Launch

---

## ✅ Authentication & User Management

### Registration
- [ ] Can register with email/password
- [ ] Email validation works (valid email format required)
- [ ] Password strength validation (min 8 chars)
- [ ] Organization auto-created on signup
- [ ] API key auto-generated
- [ ] Email verification sent (check SMTP logs)
- [ ] Cannot register with duplicate email
- [ ] Returns proper error messages

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User",
    "organization_name": "Test Org"
  }'
```

### Email Verification
- [ ] Verification email contains correct link
- [ ] Clicking link marks email as verified
- [ ] Cannot login before email verified
- [ ] Can resend verification email
- [ ] Expired tokens are rejected

### Login
- [ ] Can login with verified email
- [ ] Cannot login with wrong password
- [ ] Cannot login before email verification
- [ ] JWT token returned on success
- [ ] Token contains correct user_id
- [ ] Rate limiting works (5 attempts → locked)
- [ ] Returns user data (email, name, org)

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### API Key Authentication
- [ ] API key works in X-API-Key header
- [ ] API key works in Authorization: Bearer header
- [ ] Invalid API key returns 401
- [ ] Missing API key returns 401
- [ ] Rate limits apply per API key

**Test:**
```bash
curl -X GET http://localhost:8000/api/v1/agents \
  -H "X-API-Key: ag_live_your_key_here"
```

---

## ✅ Agents

### Create Agent
- [ ] Can create agent with JWT auth
- [ ] Can create agent with API key auth
- [ ] Agent auto-linked to user's organization
- [ ] Free plan limit enforced (max 3 agents)
- [ ] Returns 402 when limit exceeded
- [ ] Required fields validated (name)
- [ ] Optional fields accepted (endpoint_url, health_check_interval)

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/agents \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "endpoint_url": "https://example.com/agent",
    "health_check_interval": 300
  }'
```

### List Agents
- [ ] Shows only user's organization's agents
- [ ] Includes stats (traces_total, success_rate, avg_latency)
- [ ] Empty array for new users
- [ ] Pagination works (if implemented)

### Get Single Agent
- [ ] Returns agent details
- [ ] Returns 404 for non-existent agent
- [ ] Returns 404 for other org's agents (security!)
- [ ] Includes computed stats

### Update Agent
- [ ] Can update name, endpoint_url, interval
- [ ] Partial updates work
- [ ] Cannot update other org's agents
- [ ] Validates data types

### Delete Agent
- [ ] Deletes agent successfully
- [ ] Cannot delete other org's agents
- [ ] Associated traces remain (or cascade delete?)
- [ ] Returns 404 for non-existent agent

---

## ✅ Traces

### Create Trace
- [ ] Can create trace for user's agent
- [ ] Monthly limit enforced (Free: 1,000/month)
- [ ] Returns 402 when limit exceeded
- [ ] Auto-links to agent_id
- [ ] Accepts all optional fields (duration, tokens, cost)
- [ ] JSON trace_data stored correctly
- [ ] Status field validated (success/error)

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/traces \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "AGENT_UUID",
    "trace_data": {
      "input": "Test input",
      "output": "Test output",
      "steps": [{"step": 1, "tool": "test"}]
    },
    "status": "success",
    "total_duration_ms": 1500,
    "token_count": 250,
    "cost_usd": "0.015"
  }'
```

### List Traces
- [ ] Shows only user's org's traces
- [ ] Filter by agent_id works
- [ ] Filter by status works
- [ ] Pagination works (limit/offset)
- [ ] Returns total count
- [ ] Sorted by created_at desc

### Get Single Trace
- [ ] Returns trace with full data
- [ ] Includes agent_name
- [ ] Returns 404 for non-existent trace
- [ ] Cannot access other org's traces

---

## ✅ Tests

### Create Test
- [ ] Can create test manually
- [ ] Linked to agent_id
- [ ] Test limit enforced (Free: 10 tests)
- [ ] Returns 402 when limit exceeded
- [ ] Stores code correctly
- [ ] Optional source_trace_id accepted

### Generate Test from Trace
- [ ] Generates valid Python test code
- [ ] Includes mocks for API calls
- [ ] Handles success traces
- [ ] Handles error traces
- [ ] Test limit enforced
- [ ] Returns generated code

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/test-generation/from-trace \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "TRACE_UUID",
    "test_name": "test_booking_success"
  }'
```

### List Tests
- [ ] Shows only user's org's tests
- [ ] Filter by agent_id works
- [ ] Includes last_run data
- [ ] Returns agent_name

### Run Test
- [ ] Executes test code
- [ ] Creates TestRun record
- [ ] Captures success/failure
- [ ] Records duration_ms
- [ ] Captures error_message on failure

---

## ✅ Webhooks (No-Code Integration)

### Webhook Ingestion
- [ ] Accepts POST to /webhooks/ingest/{org_id}
- [ ] Validates API key
- [ ] Validates org_id matches user
- [ ] Required fields enforced (agent_name, input, output, status)
- [ ] Auto-creates agent if doesn't exist
- [ ] Creates trace successfully
- [ ] Returns trace_id and agent_id

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/ingest/YOUR_ORG_ID \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "n8n Support Agent",
    "input": "How do I reset my password?",
    "output": "Check your email for reset link",
    "status": "success",
    "duration_ms": 450,
    "steps": [
      {"step": 1, "tool": "OpenAI", "status": "success"}
    ],
    "metadata": {
      "workflow_id": "n8n_123",
      "platform": "n8n"
    }
  }'
```

---

## ✅ Mocks

### Create Mock
- [ ] Creates mock for agent
- [ ] Validates provider/endpoint fields
- [ ] Stores success/error responses
- [ ] Accepts behavior types (success, error, timeout, rate_limit)

### List Mocks
- [ ] Shows only user's org's mocks
- [ ] Filter by agent_id works

### Use Mock in Test
- [ ] Mock responses used instead of real APIs
- [ ] Saves money on test runs
- [ ] Realistic responses returned

---

## ✅ Billing & Plans

### Get Available Plans
- [ ] Returns all 8 plans (Free, Starter, Pro, Team × 2 cycles)
- [ ] Shows correct pricing
- [ ] Includes feature limits
- [ ] Checkout URLs generated with user metadata

### Current Subscription
- [ ] Shows user's current plan (defaults to Free)
- [ ] Shows next billing date (if paid)
- [ ] Shows plan features

### Plan Limits Enforcement
- [ ] **Agents:** Free (3), Starter (10), Pro (25), Team (∞)
- [ ] **Traces:** Free (1K/mo), Starter (10K/mo), Pro (50K/mo), Team (∞)
- [ ] **Tests:** Free (10), Starter (100), Pro (1K), Team (∞)
- [ ] **Rate Limit:** Free (100/day), Starter (10K/day), Pro (10K/day), Team (100K/day)

**Test hitting limits:**
```bash
# Create 4th agent on Free plan → Should fail with 402
# Create 11th agent on Starter → Should fail
# Create 1,001st trace this month on Free → Should fail
```

### DODO Webhooks
- [ ] Receives payment.succeeded webhook
- [ ] Updates user metadata with plan_id
- [ ] Updates organization plan
- [ ] Sends confirmation email

---

## ✅ Admin Panel

### Admin Access
- [ ] Only users with is_admin=true can access
- [ ] Returns 403 for non-admin users
- [ ] All admin endpoints require `require_admin` dependency

### Admin Stats
- [ ] Shows total users, orgs, revenue
- [ ] Shows growth percentages
- [ ] Active agents count

### User Management
- [ ] List all users (paginated)
- [ ] Search users by email/name
- [ ] View user details
- [ ] Cannot edit/delete users (read-only for now)

---

## ✅ Rate Limiting

### API Key Rate Limits
- [ ] Free: 100 requests/day enforced
- [ ] Starter/Pro: 10K requests/day
- [ ] Team: 100K requests/day
- [ ] Returns 429 with X-RateLimit-* headers
- [ ] Reset time shown in headers

**Test:**
```bash
# Make 101 requests in a day on Free plan
for i in {1..101}; do
  curl -X GET http://localhost:8000/api/v1/agents \
    -H "X-API-Key: YOUR_FREE_KEY"
done
# 101st request should return 429
```

### Login Rate Limiting
- [ ] Max 5 login attempts per IP per 15 minutes
- [ ] Returns error with remaining time
- [ ] Resets after timeout

---

## ✅ Security

### CORS
- [ ] Only allowed origins accepted
- [ ] OPTIONS preflight requests work
- [ ] Credentials included correctly

### Input Validation
- [ ] SQL injection attempts rejected
- [ ] XSS attempts sanitized
- [ ] Large payloads rejected (max size?)
- [ ] Invalid JSON rejected with 400

### Authorization
- [ ] Cannot access other org's resources
- [ ] Cannot delete other users' data
- [ ] API endpoints check org_id

---

## ✅ Background Jobs (Celery)

### Health Checks
- [ ] Celery workers running
- [ ] Health check tasks execute
- [ ] Agent status updated in DB
- [ ] Alerts sent on failures (if configured)

### Scheduled Tasks
- [ ] Cleanup old traces (if retention policy)
- [ ] Send daily/weekly reports (if configured)

---

## ✅ Frontend Integration

### Dashboard
- [ ] Shows agents list
- [ ] Shows traces with stats
- [ ] Shows tests
- [ ] Graphs render correctly

### API Key Management
- [ ] Can view API key
- [ ] Can regenerate API key
- [ ] New key returned on generation

### Settings
- [ ] User profile editable
- [ ] Organization name editable
- [ ] Email preferences work

---

## ✅ Error Handling

### Common Errors
- [ ] 400: Bad Request (invalid JSON, missing fields)
- [ ] 401: Unauthorized (invalid/missing API key)
- [ ] 402: Payment Required (plan limits exceeded)
- [ ] 403: Forbidden (not admin, wrong org)
- [ ] 404: Not Found (agent/trace doesn't exist)
- [ ] 429: Too Many Requests (rate limit)
- [ ] 500: Internal Server Error (logged properly)

### Error Messages
- [ ] Clear, actionable error messages
- [ ] Suggest solutions where possible
- [ ] No stack traces exposed to users

---

## ✅ Performance

### Database Queries
- [ ] No N+1 queries
- [ ] Indexes on foreign keys
- [ ] Queries under 100ms for simple reads

### API Response Times
- [ ] List agents: < 200ms
- [ ] List traces: < 300ms
- [ ] Create trace: < 150ms
- [ ] Generate test: < 2 seconds

---

## 🔧 Beta-Blocking Bugs to Fix

### Known Issues:
1. [ ] **tests.py line 322** - Missing `import re` (add to imports)
2. [ ] **Webhook x_api_key** - Parameter not properly extracted (fix Depends)

### Fixes Required:

**Fix 1: Add `import re` to tests.py**
```python
# Line 9
import re
```

**Fix 2: Fix webhook API key extraction**
```python
# In webhooks.py
from fastapi import Header

@router.post("/ingest/{org_id}")
async def ingest_trace_webhook(
    org_id: str,
    payload: dict,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
```

---

## ✅ Final Verification

### Smoke Test (5 minutes)
```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register ...

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login ...

# 3. Create agent
curl -X POST http://localhost:8000/api/v1/agents ...

# 4. Send trace
curl -X POST http://localhost:8000/api/v1/traces ...

# 5. Generate test
curl -X POST http://localhost:8000/api/v1/test-generation/from-trace ...

# 6. Verify in dashboard
open http://localhost:3000/dashboard
```

### All Green? ✅
- [ ] All endpoints return expected responses
- [ ] No 500 errors in logs
- [ ] Database migrations applied
- [ ] Redis connected
- [ ] Email sending works
- [ ] Frontend loads without console errors

---

## 📊 Metrics to Track During Beta

- Time to first trace (goal: < 5 minutes)
- API error rate (goal: < 1%)
- User retention (day 1, day 7, day 30)
- Feature adoption (% using test generation, mocks, webhooks)
- Support tickets / common issues
- Performance (p95 response times)

---

**Once all items checked, system is ready for beta! 🚀**

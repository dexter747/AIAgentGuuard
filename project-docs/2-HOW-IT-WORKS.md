# How OverseeX Works
## Complete Technical & User Guide

**Last Updated**: February 2026

---

## Overview

OverseeX is an AI agent testing and monitoring platform that works by:

1. **Capturing** execution traces from your AI agents
2. **Analyzing** patterns, failures, and coordination issues
3. **Generating** tests and mocks automatically
4. **Monitoring** agent health in real-time
5. **Alerting** you before customers notice problems

This guide explains exactly how each component works, from user onboarding to production monitoring.

---

## The 30-Second Explanation

```
Your AI Agent → OverseeX SDK → Traces Dashboard → Auto-Generated Tests → CI/CD Integration
                    ↓
              Health Monitoring → Slack/Email Alerts → Fix Issues Fast
```

**Simple Version**:
1. Add 3 lines of code to your AI agent
2. Every AI conversation is automatically recorded
3. Click "Generate Test" to create pytest tests
4. Set up alerts to know when things break
5. Ship with confidence

---

## Part 1: Getting Started (10 Minutes)

### Step 1: Sign Up

1. Go to **https://app.overseex.com**
2. Click "Start Free Trial"
3. Enter email and password
4. Choose your plan (Free tier available)

**What You Get**:
- Personal dashboard with API key
- 1,000 free traces/month
- 3 agents to monitor
- 7-day data retention

### Step 2: Get Your API Key

After signup, you'll see your dashboard:

```
┌─────────────────────────────────────────────┐
│  Welcome to OverseeX!                       │
├─────────────────────────────────────────────┤
│  Your API Key:                              │
│  ┌───────────────────────────────────────┐  │
│  │ ox_live_abc123xyz789...               │  │
│  │ [Copy] [Rotate] [Reveal]              │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Plan: Free                                 │
│  Usage: 0 / 1,000 traces this month        │
└─────────────────────────────────────────────┘
```

### Step 3: Install the SDK

**For Python (LangChain, CrewAI, raw OpenAI)**:
```bash
pip install overseex
```

**For Node.js/TypeScript**:
```bash
npm install @overseex/sdk
```

### Step 4: Add 3 Lines of Code

**Python Example**:
```python
from overseex import OverseeX

client = OverseeX(api_key="ox_live_your_key_here")

# Option A: Decorator for simple functions
@client.trace
def my_agent(query: str) -> str:
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    ).choices[0].message.content

# Option B: Context manager for complex operations
with client.span("process_request") as span:
    span.set_input({"query": user_query})
    result = complex_agent_logic(user_query)
    span.set_output(result)
```

**TypeScript Example**:
```typescript
import { OverseeX } from '@overseex/sdk';

const client = new OverseeX({ apiKey: 'ox_live_your_key_here' });

// Wrap your agent function
const tracedAgent = client.trace(async (query: string) => {
  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: query }]
  });
  return response.choices[0].message.content;
});

// Use normally - traces sent automatically
const result = await tracedAgent("What is AI?");
```

**LangChain Integration**:
```python
from overseex_langchain import OverseeXCallbackHandler
from langchain.chains import LLMChain

handler = OverseeXCallbackHandler(api_key="ox_live_xxx")
chain = LLMChain(llm=OpenAI(), callbacks=[handler])

# Every chain.run() is automatically traced
result = chain.run("Explain quantum computing")
```

**CrewAI Integration**:
```python
from overseex_crewai import OverseeXObserver
from crewai import Crew

crew = Crew(agents=[...], tasks=[...])
observer = OverseeXObserver(api_key="ox_live_xxx")
crew.add_observer(observer)

# Multi-agent coordination automatically tracked
result = crew.kickoff()
```

---

## Part 2: Understanding Traces

### What Is a Trace?

A trace is a complete record of one AI agent execution:

```json
{
  "id": "trace_abc123",
  "agent_id": "agent_xyz",
  "input_data": {
    "query": "Book a meeting for tomorrow at 2pm"
  },
  "output_data": {
    "result": "Meeting scheduled for Feb 6, 2026 at 2:00 PM",
    "actions_taken": ["checked_calendar", "created_event", "sent_email"]
  },
  "status": "success",
  "total_duration_ms": 2340,
  "token_count": 1250,
  "cost_usd": "0.04",
  "metadata": {
    "tool_calls": [
      {"tool": "google_calendar", "action": "check_availability"},
      {"tool": "google_calendar", "action": "create_event"},
      {"tool": "sendgrid", "action": "send_email"}
    ]
  },
  "created_at": "2026-02-05T10:30:00Z"
}
```

### Where Traces Appear

1. **Dashboard → Traces**: See all traces in real-time
2. **Analytics → Timeline**: Daily trace counts
3. **Analytics → Performance**: Per-agent metrics
4. **Analytics → Cost**: Token usage breakdown

### Trace Statuses

| Status | Meaning |
|--------|---------|
| `success` | Agent completed the task successfully |
| `error` | Agent encountered an error |
| `failed` | Agent failed to complete the task |
| `timeout` | Agent exceeded time limit |
| `partial` | Agent partially completed (some tools failed) |

---

## Part 3: Generating Tests

### How Test Generation Works

```
Production Trace → OverseeX AI Engine → Pytest Code
                         ↓
              Analyzes: Input, Output, Tool Calls, Status
                         ↓
              Generates: Assertions, Mocks, Edge Cases
```

### Step-by-Step Process

1. **Go to Dashboard → Traces**
2. **Select a trace** (click on any row)
3. **Click "Generate Test"** button
4. **Choose generation mode**:
   - Template-Based (Free): Fast, rule-based
   - AI-Powered ($0.02): LLM-intelligent, better assertions
5. **Review generated code**
6. **Copy to your test suite**

### What Gets Generated

```python
@pytest.mark.overseex
def test_booking_agent_happy_path():
    """
    Auto-generated from production trace
    Trace ID: abc123
    Original input: "Book a meeting for tomorrow at 2pm"
    Generated: 2026-02-05 10:35:00 UTC
    """
    with mock_tools() as mocks:
        # Setup mocks based on actual API responses
        mocks['google_calendar'].check_availability.return_value = {
            "available": True,
            "slots": ["2:00 PM", "3:00 PM", "4:00 PM"]
        }
        mocks['google_calendar'].create_event.return_value = {
            "event_id": "evt_123",
            "status": "confirmed"
        }
        mocks['sendgrid'].send_email.return_value = {
            "message_id": "msg_456"
        }
        
        # Execute agent with same input
        result = agent.run("Book a meeting for tomorrow at 2pm")
        
        # Assertions from observed behavior
        assert result is not None
        assert "scheduled" in result.lower() or "confirmed" in result.lower()
        assert mocks['google_calendar'].check_availability.called
        assert mocks['google_calendar'].create_event.called
        assert mocks['sendgrid'].send_email.called
```

### Test Generation AI Engine

**File**: `/backend/app/services/ai_test_generator.py`

The AI engine:
1. Parses trace structure (input, output, tool calls, errors)
2. Identifies what assertions make sense
3. Generates mock configurations
4. Detects edge cases from metadata
5. Produces pytest-compatible code

---

## Part 4: Smart Mocking

### Why Mocking Matters

**Without mocks** (real API calls):
- 1,000 tests × $0.55/test = **$550/month**
- Network latency: 45+ seconds total
- Can't test failure scenarios safely

**With OverseeX mocks**:
- 1,000 tests × $0.005/test = **$5/month**
- Instant responses: 2.3 seconds total
- Full failure scenario coverage

### How Smart Mocks Work

```
Your Historical Traces (50+) → Pattern Analysis → Mock Templates
                                     ↓
      Learn: Response shapes, status codes, error patterns
                                     ↓
      Generate: Realistic mocks that behave like real APIs
```

### Pre-Built Mocks

OverseeX includes 20+ pre-built mock templates:

| Category | APIs |
|----------|------|
| **LLM** | OpenAI, Anthropic, Cohere |
| **Payments** | Stripe, Square |
| **Email** | SendGrid, Mailgun, SES |
| **Calendar** | Google Calendar, Outlook |
| **Messaging** | Twilio, Slack |
| **Search** | Google, Bing |
| **Database** | Notion, Airtable |

### Failure Injection

Test how your agent handles errors:

```python
from overseex import MockEngine

mock = MockEngine()

# Test timeout handling
mock.inject_failure(
    tool="openai",
    error_type="timeout",
    probability=1.0
)

# Test rate limiting
mock.inject_failure(
    tool="stripe",
    error_type="rate_limit",
    error_code=429,
    probability=0.5  # 50% of calls fail
)

# Run your tests - agents should handle gracefully
```

---

## Part 5: Health Monitoring

### How Health Checks Work

```
OverseeX Scheduler → HTTP Probe → Your Agent Endpoint
        ↓                               ↓
   Every 5 minutes          Response or Timeout
        ↓                               ↓
   Record Result          If unhealthy → Alert
```

### Configuration

**In Dashboard → Monitoring → Add Agent**:

```yaml
Agent Name: Customer Support Bot
Endpoint URL: https://api.yourcompany.com/agent/health
Check Interval: 300  # 5 minutes
Timeout: 30 seconds
Expected Status: 200
Failure Threshold: 2  # Alert after 2 consecutive failures
```

### Health States

| State | Icon | Meaning |
|-------|------|---------|
| Healthy | ✅ | All checks passing |
| Degraded | ⚠️ | Slow responses (>2s) or partial failures |
| Unhealthy | ❌ | Consecutive failures detected |
| Unknown | ❓ | No recent check data |

### Alert Channels

Configure where alerts go:

**Email**:
```
Alert when: Agent health changes to Unhealthy
Send to: ops@yourcompany.com, cto@yourcompany.com
```

**Slack**:
```
Alert when: Error rate > 10%
Send to: #ai-alerts channel
Format: 🚨 @channel Booking Agent error rate at 15%
```

**PagerDuty**:
```
Alert when: Agent down for 10+ minutes
Severity: P1
Routing: on-call-ai-team
```

---

## Part 6: Coordination Analysis

### For Multi-Agent Systems

If you're using CrewAI, AutoGen, or custom multi-agent setups, OverseeX tracks coordination between agents.

### What Gets Detected

| Issue | Description | Example |
|-------|-------------|---------|
| **State Drift** | Agents disagree on current state | Agent A thinks order is "pending", Agent B thinks it's "shipped" |
| **Broken Assumption** | Preconditions violated | Agent B expects data that Agent A didn't provide |
| **Handoff Failure** | Delegation fails | Agent A delegated to Agent B, but B never received the task |
| **Circular Dependency** | Infinite loops | A → B → C → A → ... |
| **Duplicate Work** | Wasted effort | Both Agent A and Agent B processed the same request |

### How It Works

```
Multi-Agent Traces → Coordination Analyzer → Issue Detection
                            ↓
      Groups by: workflow_id or time window (5 min)
                            ↓
      Analyzes: State changes, handoffs, tool calls
                            ↓
      Reports: Issues with severity, affected agents, fix suggestions
```

### Viewing Issues

**Dashboard → Coordination → Issues**:

```
┌────────────────────────────────────────────────────────────┐
│ 🔴 Critical Issue Detected                                  │
├────────────────────────────────────────────────────────────┤
│ Type: State Drift                                          │
│ Severity: Critical                                         │
│ Affected Agents: Order Processor, Shipping Agent           │
│                                                            │
│ Description: Order #12345 status is "pending" in Order     │
│ Processor but "shipped" in Shipping Agent after handoff.   │
│                                                            │
│ Suggested Fix: Ensure Order Processor updates status       │
│ before delegating to Shipping Agent.                       │
│                                                            │
│ Timestamp: 2026-02-05 10:30:00 UTC                        │
└────────────────────────────────────────────────────────────┘
```

---

## Part 7: Analytics Dashboard

### Available Metrics

**Real-Time Cards**:
- Total Traces (this period)
- Success Rate (%)
- Total Errors
- Total Cost ($)

**Charts**:
1. **Traces Timeline**: Daily trace volume
2. **Agent Performance**: Duration, error rate, cost by agent
3. **Cost Breakdown**: Pie chart of spend per agent

### API Endpoints

All metrics available via API:

```bash
# Dashboard stats
GET /api/v1/analytics/dashboard/stats

# Timeline data
GET /api/v1/analytics/traces-timeline?days=30

# Agent performance
GET /api/v1/analytics/agent-performance?agent_id=xxx

# Cost breakdown
GET /api/v1/analytics/cost-breakdown
```

---

## Part 8: Regression Detection

### How It Works

```
Baseline Period (14 days) → Current Period (7 days) → Comparison
                                    ↓
                    Calculate: Error rate, duration, cost, tokens
                                    ↓
                    Detect: Deviations > threshold
                                    ↓
                    Report: "Regression detected" or "All clear"
```

### Thresholds

| Metric | Regression Threshold |
|--------|---------------------|
| Error Rate | >10% increase |
| Duration | >30% increase |
| Cost | >25% increase |
| Token Usage | >40% increase |

### CI/CD Integration

Add to your pipeline:

```yaml
# GitHub Actions example
- name: Check for Regressions
  run: |
    response=$(curl -X GET \
      "https://api.overseex.com/api/v1/regressions/detect?agent_id=$AGENT_ID" \
      -H "Authorization: Bearer $OVERSEEX_API_KEY")
    
    has_regressions=$(echo $response | jq '.has_regressions')
    
    if [ "$has_regressions" = "true" ]; then
      echo "❌ Regressions detected!"
      echo $response | jq '.regressions'
      exit 1
    fi
    
    echo "✅ No regressions detected"
```

---

## Part 9: PII Redaction

### Automatic Protection

OverseeX automatically redacts sensitive data before storage:

**Before Storage**:
```json
{
  "input": "My email is john@example.com and my SSN is 123-45-6789"
}
```

**After Redaction**:
```json
{
  "input": "My email is <EMAIL_REDACTED> and my SSN is <SSN_REDACTED>"
}
```

### What Gets Detected

- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers
- IP addresses
- Person names (via NER)
- API keys and tokens
- Medical record numbers (HIPAA mode)
- Custom patterns (Enterprise)

### Configuration

**Dashboard → Settings → Privacy**:

```yaml
PII Redaction: Enabled
Detect:
  - Email: ✅
  - Phone: ✅
  - Credit Card: ✅
  - SSN: ✅
  - IP Address: ✅
  - Person Names: ✅
  
Compliance Mode:
  - HIPAA: ❌ (Enable for healthcare)
  - GDPR: ✅
  
Pseudonymization: Enabled
# Use consistent replacements so analytics still work
# "john@example.com" → "USER_001" (same across traces)
```

---

## Part 10: API Reference

### Authentication

**Option 1: API Key (for agents/scripts)**:
```bash
curl -H "X-API-Key: ox_live_xxx" https://api.overseex.com/api/v1/agents
```

**Option 2: JWT Token (for dashboard)**:
```bash
# Login
curl -X POST https://api.overseex.com/api/v1/auth/login \
  -d '{"email": "user@example.com", "password": "xxx"}'

# Use token
curl -H "Authorization: Bearer eyJ..." https://api.overseex.com/api/v1/agents
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents` | GET, POST | List/create agents |
| `/api/v1/traces` | GET, POST | List/create traces |
| `/api/v1/tests` | GET, POST | List/create tests |
| `/api/v1/health` | GET | Health check results |
| `/api/v1/analytics/dashboard/stats` | GET | Dashboard metrics |
| `/api/v1/regressions/detect` | GET | Check for regressions |
| `/api/v1/coordination/issues` | GET | List coordination issues |

### Rate Limits

| Plan | Per Minute | Per Hour | Per Day |
|------|------------|----------|---------|
| Free | 60 | 1,000 | 10,000 |
| Pro | 300 | 10,000 | 100,000 |
| Team | 1,000 | 50,000 | 500,000 |
| Enterprise | Custom | Custom | Custom |

---

## Common Workflows

### 1. First Week Setup

```
Day 1: Sign up → Install SDK → Verify traces appearing
Day 2: Set up Slack alerts for errors
Day 3: Generate first test from production trace
Day 4: Add 5-10 tests to your CI/CD
Day 5: Configure health monitoring
Day 6-7: Review analytics, optimize costs
```

### 2. Before Every Deploy

```
1. Run: pytest tests/ --use-mocks
2. Check: OverseeX regression endpoint
3. If green → Deploy
4. If red → Review failures → Fix → Retry
```

### 3. Monthly Review

```
1. Analytics: Check success rate trend
2. Cost: Review cost-per-agent, optimize expensive ones
3. Tests: Generate new tests from recent traces
4. Mocks: Update mock patterns from new trace data
```

---

## Troubleshooting

### Traces Not Appearing

1. **Check API key**: Is it correct? Copy fresh from dashboard.
2. **Check network**: Can your server reach `api.overseex.com`?
3. **Check SDK initialization**: Is `OverseeX()` called before functions?
4. **Check logs**: Enable `debug=True` in SDK for verbose output.

### Tests Failing

1. **Mock mismatch**: Real API changed? Regenerate mocks.
2. **Assertion too strict**: Adjust assertions for LLM non-determinism.
3. **Missing mock**: Add mock for new tool your agent uses.

### Alerts Too Noisy

1. **Increase threshold**: Change from 1 failure to 2-3 consecutive.
2. **Adjust check interval**: 5 minutes might be too frequent.
3. **Filter by severity**: Only alert on Critical/High issues.

---

## Support

- **Documentation**: https://docs.overseex.com
- **Email**: support@overseex.com
- **Discord**: https://discord.gg/overseex
- **GitHub Issues**: https://github.com/overseex/overseex/issues

---

*Built for the age of autonomous AI agents.*

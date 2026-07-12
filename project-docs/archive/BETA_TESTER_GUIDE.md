# AgentGuard Beta Testing Guide

Welcome to the AgentGuard beta! This guide will help you get started testing and integrating the platform with your AI agents.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Creating Your First Agent](#creating-your-first-agent)
3. [Integration Options](#integration-options)
4. [Sending Traces](#sending-traces)
5. [Generating Tests](#generating-tests)
6. [Setting Up Monitoring](#setting-up-monitoring)
7. [Managing Mocks](#managing-mocks)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### 1. Sign Up for Beta Access

Visit **http://localhost:3000/register** (or your deployed URL)

**Required Information:**
- Full Name
- Email Address
- Password (min 8 characters)
- Organization Name (your company/team name)

**Note:** You'll receive an email verification link. Check your inbox and click the link to activate your account.

### 2. Log In

Go to **http://localhost:3000/signin** and enter your credentials.

### 3. Get Your API Key

1. Navigate to **Dashboard → Settings → API Keys**
2. Click **"Generate New Key"**
3. Copy your API key (format: `ag_live_xxxxxxxxxxxxxxxx`)
4. **Keep it secure!** You'll need this for all integrations

---

## Creating Your First Agent

An "agent" in AgentGuard represents one of your AI agents that you want to test and monitor.

### Steps:

1. **Go to Dashboard → Agents**
2. **Click "Create Agent"**
3. **Fill in the details:**
   - **Name:** `Booking Agent` (or whatever your agent does)
   - **Endpoint URL (optional):** `https://your-api.com/agent/booking` 
   - **Health Check Interval:** `300` seconds (5 minutes)

4. **Click "Create"**

**Example Agent Names:**
- `Customer Support Agent`
- `Sales Qualification Agent`
- `Email Response Agent`
- `Data Analysis Agent`

---

## Integration Options

Choose the integration method that fits your tech stack:

### Option A: Python SDK (Recommended)

**Installation:**
```bash
pip install -e /path/to/AgentGaurd/sdk/python
```

**Basic Usage:**
```python
from agentguard import AgentGuard

# Initialize with your API key
guard = AgentGuard(api_key="ag_live_your_key_here")

# Wrap your agent function
@guard.trace(agent_name="Booking Agent")
def my_agent_function(user_input):
    # Your agent logic here
    result = call_openai(user_input)
    return result

# Run your agent - traces are sent automatically
response = my_agent_function("Book a meeting for tomorrow")
```

**What gets tracked:**
- ✅ Input/output data
- ✅ Execution time
- ✅ Success/failure status
- ✅ Token usage (if using LLMs)
- ✅ API calls made

---

### Option B: JavaScript/TypeScript SDK

**Installation:**
```bash
npm install /path/to/AgentGaurd/sdk/javascript
```

**Basic Usage:**
```typescript
import { AgentGuard } from '@agentguard/sdk';

const guard = new AgentGuard({
  apiKey: 'ag_live_your_key_here'
});

// Wrap your agent
async function bookingAgent(input: string) {
  const trace = guard.startTrace('Booking Agent');
  
  try {
    const result = await yourAgentLogic(input);
    trace.success(result);
    return result;
  } catch (error) {
    trace.error(error);
    throw error;
  }
}
```

---

### Option C: Direct API Integration

**Send traces via REST API:**

```bash
curl -X POST http://localhost:8000/api/v1/traces \
  -H "X-API-Key: ag_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "your-agent-uuid",
    "trace_data": {
      "input": "Book a meeting for tomorrow",
      "output": "Meeting booked for Jan 25, 2pm",
      "steps": [
        {"tool": "calendar_api", "result": "success"},
        {"tool": "email_sender", "result": "sent"}
      ]
    },
    "status": "success",
    "total_duration_ms": 2300,
    "token_count": 450,
    "cost_usd": "0.023"
  }'
```

---

## Sending Traces

### What to Include in Trace Data

**Minimum Required:**
```json
{
  "agent_id": "uuid-of-your-agent",
  "trace_data": {
    "input": "User's query",
    "output": "Agent's response"
  },
  "status": "success"  // or "error"
}
```

**Recommended (for better insights):**
```json
{
  "agent_id": "uuid-of-your-agent",
  "trace_data": {
    "input": "Book a flight to Paris",
    "output": "Flight booked for Feb 1st, AF123",
    "steps": [
      {
        "step": 1,
        "tool": "search_flights",
        "input": {"destination": "Paris", "date": "2026-02-01"},
        "output": {"flights": [...]},
        "duration_ms": 450
      },
      {
        "step": 2,
        "tool": "book_flight",
        "input": {"flight_id": "AF123"},
        "output": {"confirmation": "ABC123"},
        "duration_ms": 850
      }
    ],
    "llm_calls": [
      {
        "model": "gpt-4",
        "prompt_tokens": 350,
        "completion_tokens": 120,
        "cost": 0.018
      }
    ]
  },
  "status": "success",
  "total_duration_ms": 2300,
  "token_count": 470,
  "cost_usd": "0.018"
}
```

### Test Data to Send

**Send at least 5-10 traces covering:**

1. ✅ **Happy path** - Everything works perfectly
2. ✅ **Error cases** - API failures, validation errors
3. ✅ **Edge cases** - Unusual inputs, missing data
4. ✅ **Timeout scenarios** - Slow API responses
5. ✅ **Rate limit hits** - When external APIs reject requests

**Example Test Scenarios:**

| Scenario | Input | Expected Status |
|----------|-------|-----------------|
| Normal booking | "Book meeting tomorrow 2pm" | success |
| Invalid date | "Book meeting yesterday" | error |
| API timeout | (slow external API) | error |
| Missing info | "Book meeting" (no time) | error |
| Rate limited | (after many requests) | error |

---

## Generating Tests

Once you have traces in the system:

### Via Dashboard:

1. **Go to Dashboard → Agents → [Your Agent]**
2. **Click "Traces" tab**
3. **Select a trace**
4. **Click "Generate Test"**
5. **Review the generated Python test code**
6. **Click "Save Test"**

### Via API:

```bash
curl -X POST http://localhost:8000/api/v1/test-generation/from-trace \
  -H "X-API-Key: ag_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "uuid-of-trace",
    "test_name": "test_booking_happy_path"
  }'
```

**The generated test will:**
- ✅ Mock external API calls
- ✅ Validate agent behavior
- ✅ Check success/error handling
- ✅ Be ready to run with pytest

---

## Setting Up Monitoring

### Health Checks

1. **Go to Dashboard → Agents → [Your Agent] → Settings**
2. **Enable Health Monitoring**
3. **Set check interval:** `300` seconds (5 min)
4. **Add endpoint URL:** Your agent's health check endpoint

**What gets monitored:**
- Agent availability (up/down)
- Response time
- Success rate
- Error patterns

### Alerts (Coming Soon in Beta)

Configure email/Slack notifications when:
- Agent goes down
- Error rate > 10%
- Response time > 5 seconds
- Rate limits exceeded

---

## Managing Mocks

Mocks help you test without hitting real APIs (save money!).

### Create a Mock:

1. **Go to Dashboard → Agents → [Your Agent] → Mocks**
2. **Click "Create Mock"**
3. **Fill in:**

```
Name: Stripe Payment Mock
Provider: stripe
Endpoint Pattern: /v1/charges
Mock Behavior: success

Success Response:
{
  "id": "ch_mock123",
  "amount": 2000,
  "status": "succeeded"
}

Error Response (if behavior = error):
{
  "error": {
    "message": "Card declined",
    "type": "card_error"
  }
}
```

### Available Mock Behaviors:
- `success` - Returns success response
- `error` - Returns error response  
- `timeout` - Simulates slow/timeout
- `rate_limit` - Returns 429 status

### Using Mocks in Tests:

```python
# In your test file
@pytest.fixture
def use_mocks():
    # AgentGuard automatically uses mocks when running tests
    yield

def test_payment_with_mock(use_mocks):
    result = agent.process_payment(amount=20.00)
    assert result.status == "succeeded"
    # No real Stripe API call made! 💰
```

---

## Troubleshooting

### Common Issues:

#### 1. "Invalid API Key" Error

**Solution:**
- Check your API key is correctly copied
- Verify it starts with `ag_live_`
- Regenerate if needed from Settings → API Keys

#### 2. "Agent not found" Error

**Solution:**
- Get your agent ID from Dashboard → Agents
- Use the correct UUID in API calls
- Verify agent belongs to your organization

#### 3. Traces Not Appearing

**Solution:**
- Check API response status (should be 201)
- Verify `agent_id` is correct
- Check `trace_data` is valid JSON
- Look at browser console/logs for errors

#### 4. Rate Limit Exceeded (429 Error)

**Your current plan limits:**
- **Free:** 100 API calls/day, 3 agents, 1K traces/month
- **Starter:** 10K calls/day, 10 agents, 10K traces/month
- **Pro:** 10K calls/day, 25 agents, 50K traces/month

**Solution:** Upgrade plan or wait for limit reset

#### 5. Email Verification Not Received

**Solution:**
- Check spam folder
- Resend verification from login page
- Contact support if still missing

---

## Beta Testing Checklist

Please test these workflows:

### Week 1: Basic Setup
- [ ] Sign up and verify email
- [ ] Create API key
- [ ] Create first agent
- [ ] Send 10+ test traces (mix of success/error)
- [ ] View traces in dashboard

### Week 2: Test Generation
- [ ] Generate test from a successful trace
- [ ] Generate test from an error trace
- [ ] Run generated test locally
- [ ] Create custom test manually

### Week 3: Monitoring & Mocks
- [ ] Set up health check for agent
- [ ] Create mock for external API
- [ ] Test with mocked responses
- [ ] View analytics dashboard

### Week 4: Advanced Features
- [ ] Generate full test suite (5+ tests)
- [ ] Test rate limiting behavior
- [ ] Integrate with CI/CD (optional)
- [ ] Try webhook notifications

---

## Sample Test Data

Here's a complete example you can copy-paste to test the system:

### 1. Create Agent via Dashboard
```
Name: Demo Booking Agent
Endpoint URL: https://demo.example.com/booking
Health Check Interval: 300
```

### 2. Send Sample Traces via API

**Success Case:**
```bash
curl -X POST http://localhost:8000/api/v1/traces \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "YOUR_AGENT_ID",
    "trace_data": {
      "input": "Book a meeting room for tomorrow 2pm",
      "output": "Conference Room A booked for Jan 25, 2026 at 2:00 PM",
      "steps": [
        {"tool": "check_availability", "status": "success", "duration_ms": 150},
        {"tool": "create_booking", "status": "success", "duration_ms": 200},
        {"tool": "send_confirmation", "status": "success", "duration_ms": 100}
      ]
    },
    "status": "success",
    "total_duration_ms": 450
  }'
```

**Error Case:**
```bash
curl -X POST http://localhost:8000/api/v1/traces \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "YOUR_AGENT_ID",
    "trace_data": {
      "input": "Book a meeting room for yesterday",
      "output": null,
      "error": "Cannot book in the past",
      "steps": [
        {"tool": "validate_date", "status": "error", "error": "Invalid date"}
      ]
    },
    "status": "error",
    "total_duration_ms": 50
  }'
```

---

## Support & Feedback

### Getting Help:
- 📧 Email: support@agentguard.ai
- 💬 Slack: [Beta Tester Channel]
- 🐛 Issues: GitHub Issues (link)

### Feedback Form:
We'd love your input! Please share:
- What features work well?
- What's confusing or broken?
- What features are you missing?
- Any bugs you encounter?

**Feedback Survey:** [Link to form]

---

## API Reference

For detailed API documentation, visit:
- **API Docs:** http://localhost:8000/docs (Swagger)
- **Full Docs:** `/docs/API.md` in the repo

---

## What's Next?

After beta testing, we'll launch:
- 🔔 Email/Slack alerts
- 📊 Advanced analytics dashboards
- 🔄 CI/CD integrations (GitHub Actions, CircleCI)
- 🎯 Regression detection
- 👥 Team collaboration features
- 🔐 SSO/SAML for enterprises

Thank you for helping us build AgentGuard! 🚀

---

**Questions?** Don't hesitate to reach out. We're here to help!

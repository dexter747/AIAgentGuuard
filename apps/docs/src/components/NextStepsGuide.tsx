// Next Steps Guide Component
import { Shield, Eye, TestTube, Zap, Bell, TrendingUp } from 'lucide-react'

export default function NextStepsGuide() {
  const steps = [
    {
      number: 1,
      title: "Install & Instrument",
      icon: Shield,
      time: "5 minutes",
      description: "Add OverseeX SDK to your AI code",
      code: `from overseex import OverseeX, instrument_framework

client = OverseeX(api_key="ag_live_xxx")
instrument_framework(client, "auto")  # Done!`,
      outcome: "✅ Every AI call now traced automatically"
    },
    {
      number: 2,
      title: "View Real-Time Traces",
      icon: Eye,
      time: "24 hours",
      description: "Watch your AI work in the dashboard",
      tasks: [
        "Verify traces appearing correctly",
        "Identify common query patterns",
        "Spot any errors or failures",
        "Check token costs and timing"
      ],
      outcome: "✅ Full visibility into AI behavior"
    },
    {
      number: 3,
      title: "Set Up Monitoring",
      icon: Bell,
      time: "15 minutes",
      description: "Get instant alerts when things break",
      alerts: [
        "Error rate > 10% → Slack notification",
        "Response time > 5s → Email team",
        "Daily cost > $50 → SMS alert",
        "Specific errors → Create Jira ticket"
      ],
      outcome: "✅ Problems detected before customers complain"
    },
    {
      number: 4,
      title: "Generate Tests",
      icon: TestTube,
      time: "Ongoing",
      description: "Auto-create tests from production traces",
      workflow: [
        "Click any trace in dashboard",
        "Click 'Generate Test' button",
        "Choose template-based (free) or AI-powered ($0.02)",
        "Copy generated pytest code",
        "Add to your test suite",
        "Run before every deploy"
      ],
      outcome: "✅ Comprehensive test suite with zero manual work"
    },
    {
      number: 5,
      title: "Create Smart Mocks",
      icon: Zap,
      time: "30 minutes",
      description: "Eliminate testing costs with learned mocks",
      savings: {
        realAPIs: "$500/month",
        withMocks: "$5/month",
        saved: "$495/month"
      },
      workflow: [
        "Dashboard → Mocks → Generate from Agent",
        "OverseeX learns patterns from traces",
        "Download mock configurations",
        "Add to tests/mocks.py",
        "Tests now cost $0 instead of $0.03/call"
      ],
      outcome: "✅ 100x cheaper testing"
    },
    {
      number: 6,
      title: "Deploy with Confidence",
      icon: TrendingUp,
      time: "Every release",
      description: "Run tests before deploying changes",
      command: "pytest tests/ --use-mocks",
      results: {
        tests: "47 passed",
        time: "2.3s",
        cost: "$0",
        confidence: "100%"
      },
      outcome: "✅ Zero AI breaks in production"
    }
  ]

  return (
    <div className="next-steps-guide">
      {steps.map((step) => (
        <StepCard key={step.number} {...step} />
      ))}
    </div>
  )
}

function StepCard({ number, title, icon: Icon, time, description, outcome, ...props }) {
  return (
    <div className="step-card">
      <div className="step-header">
        <div className="step-number">{number}</div>
        <Icon className="step-icon" />
        <h3>{title}</h3>
        <span className="step-time">{time}</span>
      </div>
      <p className="step-description">{description}</p>
      
      {props.code && (
        <pre className="code-block">{props.code}</pre>
      )}
      
      {props.tasks && (
        <ul className="task-list">
          {props.tasks.map((task, i) => (
            <li key={i}>• {task}</li>
          ))}
        </ul>
      )}
      
      {props.alerts && (
        <div className="alerts-list">
          {props.alerts.map((alert, i) => (
            <div key={i} className="alert-item">🔔 {alert}</div>
          ))}
        </div>
      )}
      
      {props.workflow && (
        <ol className="workflow-list">
          {props.workflow.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      )}
      
      {props.savings && (
        <div className="savings-card">
          <div className="savings-item">
            <span className="label">Real APIs:</span>
            <span className="value negative">{props.savings.realAPIs}</span>
          </div>
          <div className="savings-item">
            <span className="label">With Mocks:</span>
            <span className="value positive">{props.savings.withMocks}</span>
          </div>
          <div className="savings-total">
            💰 Save {props.savings.saved}
          </div>
        </div>
      )}
      
      {props.command && (
        <div className="command-block">
          <code>$ {props.command}</code>
          {props.results && (
            <div className="command-results">
              <div>✅ {props.results.tests}</div>
              <div>⏱️  {props.results.time}</div>
              <div>💰 Cost: {props.results.cost}</div>
              <div>🎯 Confidence: {props.results.confidence}</div>
            </div>
          )}
        </div>
      )}
      
      <div className="step-outcome">{outcome}</div>
    </div>
  )
}

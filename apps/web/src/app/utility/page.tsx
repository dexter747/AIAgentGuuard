'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Activity, 
  ArrowRight, 
  Check, 
  Code2, 
  Zap,
  TestTube,
  Bell,
  Shield,
  Bot,
  Server,
  Users,
  Workflow,
  FileCode,
  Gauge,
  Lock,
  LineChart,
  AlertTriangle,
  Layers,
  Sparkles
} from 'lucide-react'
import { Navbar } from '@/components/Navbar'

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

const corePillars = [
  { icon: Activity, title: 'Trace Capture', desc: 'Record every AI agent execution for analysis and debugging' },
  { icon: TestTube, title: 'Test Generation', desc: 'Auto-generate pytest tests from production traces' },
  { icon: Server, title: 'Mock Engine', desc: 'Mock APIs to cut testing costs by 95%' },
  { icon: Bell, title: 'Health Monitoring', desc: 'Proactive alerts before customers notice failures' },
  { icon: Users, title: 'Coordination Analysis', desc: 'Detect failures in multi-agent systems' },
  { icon: LineChart, title: 'Analytics & Cost', desc: 'Track performance, tokens, and spend' },
]

const keyFeatures = [
  { icon: Zap, title: 'AI-Powered Tests', desc: 'LLM-intelligent test creation from real traces', highlight: true },
  { icon: Shield, title: 'PII Redaction', desc: 'HIPAA/GDPR compliant with auto redaction', highlight: false },
  { icon: Layers, title: '20+ Pre-Built Mocks', desc: 'OpenAI, Stripe, SendGrid, Slack & more', highlight: true },
  { icon: AlertTriangle, title: 'Regression Detection', desc: 'Block deploys when agent behavior degrades', highlight: false },
  { icon: Workflow, title: 'Framework Agnostic', desc: 'LangChain, CrewAI, AutoGen supported', highlight: false },
  { icon: Code2, title: 'Multi-SDK Support', desc: 'Python, TypeScript, JavaScript SDKs', highlight: false },
]

const useCases = [
  {
    icon: TestTube,
    title: 'QA Team Testing AI Bots',
    persona: 'QA Engineer',
    challenge: 'Writing tests manually takes weeks, real API testing costs $500+/month',
    solution: 'Auto-generate tests from production traces with mocked APIs',
    results: ['Testing: 2 weeks → 2 hours', 'Cost: $500/mo → $5/mo', 'Detection: 2hr → 5min'],
  },
  {
    icon: Bot,
    title: 'Startup AI Sales Agent',
    persona: 'Full-stack Developer',
    challenge: 'One engineer, no time for testing, agent calls 5+ APIs',
    solution: 'Quick SDK setup, auto-test generation, cost optimization',
    results: ['Visibility: 0% → 100%', 'Coverage: 5% → 80%', 'AI cost: $600 → $200/mo'],
  },
  {
    icon: Users,
    title: 'Enterprise Multi-Agent Systems',
    persona: 'AI Platform Lead',
    challenge: 'Agents pass work incorrectly, compliance requires audit trails',
    solution: 'Coordination analysis, HIPAA mode, 365-day retention',
    results: ['Detection: 2hr → 5min', 'Compliance: Always ready', 'Reliability: 95% → 99.5%'],
  },
  {
    icon: Workflow,
    title: 'No-Code AI Workflows',
    persona: 'Marketing Ops Manager',
    challenge: 'No way to know if n8n/Make workflow fails, can\'t debug alone',
    solution: 'Webhook integration, dashboard visibility, instant alerts',
    results: ['Visibility: None → Full', 'Debug: Hours → Minutes', 'Cost tracking: $2.50/post'],
  },
  {
    icon: FileCode,
    title: 'AI Coding Assistant',
    persona: 'Engineering Manager',
    challenge: 'Code suggestions wrong, hard to test all language combos',
    solution: 'Language-specific test generation, performance monitoring',
    results: ['Coverage: 1000 tests', 'Cost: $5/run vs $500', 'Quality regression: Auto'],
  },
  {
    icon: Lock,
    title: 'Healthcare AI Compliance',
    persona: 'Chief Medical AI Officer',
    challenge: 'HIPAA compliance mandatory, patient data in traces',
    solution: 'HIPAA mode, auto redaction, audit trails, 365-day retention',
    results: ['HIPAA: Maintained', 'Audit: Real-time', 'Protection: Automatic'],
  },
]

const integrations = [
  { name: 'LangChain', type: 'Framework' },
  { name: 'CrewAI', type: 'Framework' },
  { name: 'AutoGen', type: 'Framework' },
  { name: 'n8n', type: 'No-Code' },
  { name: 'Make.com', type: 'No-Code' },
  { name: 'Zapier', type: 'No-Code' },
  { name: 'Python SDK', type: 'Native' },
  { name: 'TypeScript SDK', type: 'Native' },
]

export default function UtilityPage() {
  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      
      <main className="pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-20"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-violet-500/10 border border-violet-500/30 mb-6">
              <Sparkles className="w-8 h-8 text-violet-400" />
            </div>
            <h1 className="text-5xl md:text-6xl font-medium mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              What is OverseeX?
            </h1>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto font-medium">
              The complete AI agent testing & monitoring platform. Auto-generate tests, mock expensive APIs, 
              monitor health 24/7, and ship with confidence.
            </p>
          </motion.div>

          {/* Core Pillars */}
          <motion.section
            {...fadeIn}
            transition={{ delay: 0.1 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-8 text-center">Six Core Pillars</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {corePillars.map((pillar, i) => (
                <motion.div
                  key={pillar.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + i * 0.05 }}
                  className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-violet-500/30 transition-all"
                >
                  <pillar.icon className="w-10 h-10 text-violet-400 mb-4" />
                  <h3 className="text-white font-medium text-lg mb-2">{pillar.title}</h3>
                  <p className="text-gray-400 font-medium">{pillar.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Key Features */}
          <motion.section
            {...fadeIn}
            transition={{ delay: 0.2 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-4 text-center">Key Features</h2>
            <p className="text-gray-400 text-center mb-8 font-medium max-w-2xl mx-auto">
              Everything you need to test, monitor, and optimize your AI agents
            </p>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {keyFeatures.map((feature, i) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + i * 0.05 }}
                  className={`p-5 rounded-xl border transition-all ${
                    feature.highlight 
                      ? 'bg-violet-500/10 border-violet-500/30' 
                      : 'bg-white/5 border-white/10'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <feature.icon className={`w-6 h-6 ${feature.highlight ? 'text-violet-400' : 'text-gray-400'}`} />
                    <div>
                      <h3 className="text-white font-medium mb-1">{feature.title}</h3>
                      <p className="text-gray-400 text-sm font-medium">{feature.desc}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* How It Works - Simple */}
          <motion.section
            {...fadeIn}
            transition={{ delay: 0.25 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-8 text-center">How It Works</h2>
            <div className="grid md:grid-cols-4 gap-6">
              {[
                { step: '1', title: 'Instrument', desc: 'Add SDK in 3 lines of code' },
                { step: '2', title: 'Capture', desc: 'Every agent execution is recorded' },
                { step: '3', title: 'Generate', desc: 'Click to create tests with mocks' },
                { step: '4', title: 'Monitor', desc: '24/7 health checks & alerts' },
              ].map((item, i) => (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.25 + i * 0.1 }}
                  className="relative"
                >
                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10 h-full">
                    <div className="w-10 h-10 rounded-xl bg-violet-500/20 border border-violet-500/30 flex items-center justify-center mb-4">
                      <span className="text-violet-400 font-medium">{item.step}</span>
                    </div>
                    <h3 className="text-white font-medium mb-2">{item.title}</h3>
                    <p className="text-gray-400 text-sm font-medium">{item.desc}</p>
                  </div>
                  {i < 3 && (
                    <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                      <ArrowRight className="w-6 h-6 text-gray-600" />
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Use Cases */}
          <motion.section
            {...fadeIn}
            transition={{ delay: 0.3 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-4 text-center">Real-World Use Cases</h2>
            <p className="text-gray-400 text-center mb-10 font-medium max-w-2xl mx-auto">
              See how teams across industries use OverseeX to ship AI agents with confidence
            </p>
            <div className="grid lg:grid-cols-2 gap-6">
              {useCases.map((useCase, i) => (
                <motion.div
                  key={useCase.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + i * 0.05 }}
                  className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-violet-500/20 transition-all"
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center flex-shrink-0">
                      <useCase.icon className="w-6 h-6 text-violet-400" />
                    </div>
                    <div>
                      <h3 className="text-white font-medium text-lg">{useCase.title}</h3>
                      <p className="text-violet-400 text-sm font-medium">{useCase.persona}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3 mb-4">
                    <div>
                      <span className="text-gray-500 text-xs font-medium uppercase tracking-wide">Challenge</span>
                      <p className="text-gray-400 text-sm font-medium">{useCase.challenge}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 text-xs font-medium uppercase tracking-wide">Solution</span>
                      <p className="text-gray-300 text-sm font-medium">{useCase.solution}</p>
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {useCase.results.map((result, j) => (
                      <span
                        key={j}
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium"
                      >
                        <Check className="w-3 h-3" />
                        {result}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Integrations */}
          <motion.section
            {...fadeIn}
            transition={{ delay: 0.4 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-4 text-center">Works With Everything</h2>
            <p className="text-gray-400 text-center mb-8 font-medium">
              Native integrations for popular frameworks and no-code tools
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              {integrations.map((int, i) => (
                <motion.div
                  key={int.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 + i * 0.05 }}
                  className="px-5 py-3 rounded-xl bg-white/5 border border-white/10"
                >
                  <span className="text-white font-medium">{int.name}</span>
                  <span className="text-gray-500 text-xs ml-2 font-medium">{int.type}</span>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Stats */}
          <motion.section
            {...fadeIn}
            transition={{ delay: 0.45 }}
            className="mb-20"
          >
            <div className="grid md:grid-cols-4 gap-6">
              {[
                { value: '95%', label: 'Cost Reduction' },
                { value: '5 min', label: 'Setup Time' },
                { value: '20+', label: 'Pre-Built Mocks' },
                { value: '24/7', label: 'Monitoring' },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.45 + i * 0.1 }}
                  className="text-center p-6 rounded-2xl bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/20"
                >
                  <div className="text-4xl font-medium text-white mb-2">{stat.value}</div>
                  <div className="text-gray-400 font-medium">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* CTA */}
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.5 }}
            className="text-center p-12 rounded-2xl bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/20"
          >
            <h2 className="text-3xl font-medium text-white mb-4">Ready to ship AI agents with confidence?</h2>
            <p className="text-gray-400 mb-8 font-medium">Start testing and monitoring in minutes. Free tier available.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="px-8 py-4 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors inline-flex items-center justify-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/pricing"
                className="px-8 py-4 bg-white/10 text-white font-medium rounded-xl hover:bg-white/20 transition-colors"
              >
                View Pricing
              </Link>
            </div>
          </motion.div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm font-medium">
            © 2026 OverseeX. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

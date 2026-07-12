'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Puzzle, ArrowRight, Check, Code2, Zap, Package } from 'lucide-react'
import { Navbar } from '@/components/Navbar'

export default function IntegrationsPage() {
  return (
    <div className="min-h-screen bg-black">
      <Navbar />

      <main className="pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-violet-500/10 border border-violet-500/30 mb-6">
              <Puzzle className="w-8 h-8 text-violet-400" />
            </div>
            <h1 className="text-5xl md:text-6xl font-medium mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Framework Integrations
            </h1>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              One-line integrations for CrewAI, LangChain, LangGraph, and more. Zero-config auto-instrumentation.
            </p>
          </motion.div>

          {/* Supported Frameworks */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">Supported Frameworks</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  name: 'CrewAI',
                  desc: 'Auto-capture crew task delegation, agent handoffs, and tool calls',
                  code: `from overseex_crewai import monitor_crew

crew = Crew(agents=[...], tasks=[...])
monitor_crew(crew, api_key="ag_live_...")`,
                  status: 'Available'
                },
                {
                  name: 'LangChain',
                  desc: 'Callback handler for chains, agents, and tools with full context',
                  code: `from overseex_langchain import OverseeXCallback

chain = LLMChain(
  llm=...,
  callbacks=[OverseeXCallback()]
)`,
                  status: 'Available'
                },
                {
                  name: 'LangGraph',
                  desc: 'State graph workflow monitoring with visual debugging',
                  code: `from overseex_langchain import OverseeXGraphMonitor

graph = StateGraph(...)
monitor = OverseeXGraphMonitor(graph)`,
                  status: 'Available'
                }
              ].map((framework, i) => (
                <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/10">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-white font-medium text-lg">{framework.name}</h3>
                    <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">
                      {framework.status}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm mb-4">{framework.desc}</p>
                  <div className="bg-black/50 rounded-lg p-3 font-mono text-xs text-gray-400 overflow-x-auto">
                    <pre>{framework.code}</pre>
                  </div>
                </div>
              ))}
            </div>
          </motion.section>

          {/* What It Is */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">Why Native Integrations?</h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-6">
              Generic tracing misses framework-specific context. Our native plugins understand CrewAI crew dynamics,
              LangChain callback events, and LangGraph state transitions at a deep level. This means richer traces,
              better coordination analysis, and more accurate fix suggestions.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { icon: Zap, title: 'Zero Config', desc: 'One line of code to start capturing. No manual instrumentation required.' },
                { icon: Code2, title: 'Rich Context', desc: 'Capture framework-specific metadata like crew roles, chain steps, and graph states.' },
                { icon: Package, title: 'PyPI Packages', desc: 'Simple pip install with automatic dependency handling.' }
              ].map((item, i) => (
                <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/10">
                  <item.icon className="w-8 h-8 text-violet-400 mb-4" />
                  <h3 className="text-white font-medium mb-2">{item.title}</h3>
                  <p className="text-gray-400 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </motion.section>

          {/* Installation */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">Quick Start</h2>
            <div className="space-y-6">
              {[
                { step: '1', title: 'Install the package', code: 'pip install overseex-crewai  # or overseex-langchain' },
                { step: '2', title: 'Add one line of code', code: 'monitor_crew(crew, api_key="ag_live_xxx")' },
                { step: '3', title: 'Run your agent', code: 'crew.kickoff()  # Traces captured automatically!' }
              ].map((item) => (
                <div key={item.step} className="flex gap-6 items-start p-6 rounded-2xl bg-white/5 border border-white/10">
                  <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-violet-400 font-medium">{item.step}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-white font-medium mb-2">{item.title}</h3>
                    <div className="bg-black/50 rounded-lg p-3 font-mono text-sm text-gray-400">
                      {item.code}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.section>

          {/* Use Cases */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">What Gets Captured</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { title: 'Agent Handoffs', desc: 'Track when one agent delegates work to another' },
                { title: 'Tool Invocations', desc: 'Capture tool inputs, outputs, and timing' },
                { title: 'LLM Calls', desc: 'Full prompt/response pairs with token counts' },
                { title: 'State Changes', desc: 'Track state evolution in LangGraph workflows' },
                { title: 'Error Propagation', desc: 'See exactly where failures originate and spread' },
                { title: 'Memory Updates', desc: 'Monitor agent memory and context changes' }
              ].map((item, i) => (
                <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/10">
                  <Check className="w-6 h-6 text-emerald-400 mb-3" />
                  <h3 className="text-white font-medium mb-2">{item.title}</h3>
                  <p className="text-gray-400 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </motion.section>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-center p-12 rounded-2xl bg-gradient-to-br from-violet-500/10 to-purple-500/10 border border-violet-500/20"
          >
            <h2 className="text-3xl font-medium text-white mb-4">Get started in 2 minutes</h2>
            <p className="text-gray-400 mb-8">One line of code. Full observability.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="px-8 py-4 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors inline-flex items-center justify-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/docs#integrations"
                className="px-8 py-4 bg-white/10 text-white font-medium rounded-xl hover:bg-white/20 transition-colors"
              >
                Read Documentation
              </Link>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}

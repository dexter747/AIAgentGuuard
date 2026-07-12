'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Network, ArrowRight, Check, GitBranch, Eye, AlertTriangle } from 'lucide-react'
import { Navbar } from '@/components/Navbar'

export default function CoordinationPage() {
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
              <Network className="w-8 h-8 text-violet-400" />
            </div>
            <h1 className="text-5xl md:text-6xl font-medium mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Multi-Agent Coordination
            </h1>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Visualize, debug, and optimize how your AI agents work together with advanced coordination intelligence.
            </p>
          </motion.div>

          {/* What It Is */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">What is Coordination Analysis?</h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-6">
              Multi-agent systems are powerful but complex. When agents hand off work, share state, or make assumptions
              about each other, things can fail silently. Coordination Analysis gives you X-ray vision into how your
              agents interact, detecting state drift, broken handoffs, and coordination failures before they become production issues.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { icon: GitBranch, title: 'State Drift Detection', desc: 'Automatically detect when state becomes inconsistent between agent handoffs' },
                { icon: Eye, title: 'Visual Flow Diagrams', desc: 'Interactive React Flow graphs showing agent interactions in real-time' },
                { icon: AlertTriangle, title: 'Handoff Failure Analysis', desc: 'Identify failed handoffs with clear root cause and suggested fixes' }
              ].map((item, i) => (
                <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/10">
                  <item.icon className="w-8 h-8 text-violet-400 mb-4" />
                  <h3 className="text-white font-medium mb-2">{item.title}</h3>
                  <p className="text-gray-400 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </motion.section>

          {/* How It Works */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">How It Works</h2>
            <div className="space-y-6">
              {[
                { step: '1', title: 'Capture Multi-Agent Traces', desc: 'Use our SDKs or framework integrations to automatically capture agent interactions' },
                { step: '2', title: 'Analyze Coordination Patterns', desc: 'Our ML engine detects state drift, broken assumptions, and handoff failures' },
                { step: '3', title: 'Visualize & Debug', desc: 'Interactive flow diagrams show exactly where coordination broke down' },
                { step: '4', title: 'Apply Fixes', desc: 'Get AI-powered suggestions to fix coordination issues with one click' }
              ].map((item) => (
                <div key={item.step} className="flex gap-6 items-start p-6 rounded-2xl bg-white/5 border border-white/10">
                  <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center flex-shrink-0">
                    <span className="text-violet-400 font-medium">{item.step}</span>
                  </div>
                  <div>
                    <h3 className="text-white font-medium mb-2">{item.title}</h3>
                    <p className="text-gray-400">{item.desc}</p>
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
            <h2 className="text-3xl font-medium text-white mb-6">Use Cases</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { title: 'CrewAI Debugging', desc: 'Visualize crew task delegation and agent handoffs in real-time' },
                { title: 'LangGraph Workflows', desc: 'Debug complex state graphs with visual flow diagrams' },
                { title: 'Multi-Agent Orchestration', desc: 'Monitor coordination between multiple autonomous agents' },
                { title: 'Failure Root Cause', desc: 'Instantly identify which agent or handoff caused a workflow failure' }
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
            <h2 className="text-3xl font-medium text-white mb-4">Debug multi-agent systems like never before</h2>
            <p className="text-gray-400 mb-8">Get visual coordination intelligence for your AI agents.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="px-8 py-4 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors inline-flex items-center justify-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/docs#coordination"
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

'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Sparkles, ArrowRight, Check, Brain, ThumbsUp, Lightbulb } from 'lucide-react'
import { Navbar } from '@/components/Navbar'

export default function CorrectivePage() {
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
              <Sparkles className="w-8 h-8 text-violet-400" />
            </div>
            <h1 className="text-5xl md:text-6xl font-medium mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Corrective Intelligence
            </h1>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              ML-powered fix suggestions that learn from your feedback to automatically suggest corrections for agent failures.
            </p>
          </motion.div>

          {/* What It Is */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">What is Corrective Intelligence?</h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-6">
              When your AI agents fail, you shouldn't have to guess at the fix. Corrective Intelligence analyzes failed
              traces, compares them to successful patterns, and suggests specific code changes to fix the issue. Best of all,
              it learns from your feedback—approve or reject suggestions to make the system smarter over time.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { icon: Brain, title: 'ML-Powered Analysis', desc: 'Deep learning models trained on millions of agent execution patterns' },
                { icon: ThumbsUp, title: 'Feedback Loop', desc: 'Approve or reject suggestions to personalize recommendations to your codebase' },
                { icon: Lightbulb, title: 'Proactive Suggestions', desc: 'Get fix recommendations before issues impact production' }
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
                { step: '1', title: 'Detect Failure Patterns', desc: 'Our ML engine identifies common failure patterns in your agent traces' },
                { step: '2', title: 'Generate Corrections', desc: 'AI suggests specific code changes, config tweaks, or workflow modifications' },
                { step: '3', title: 'Review & Approve', desc: 'Simple thumbs up/down interface to accept or reject suggestions' },
                { step: '4', title: 'Continuous Learning', desc: 'Your feedback trains the model to give better suggestions over time' }
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

          {/* Example Suggestion */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">Example Suggestion</h2>
            <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="w-5 h-5 text-violet-400" />
                <span className="text-white font-medium">Suggested Fix: Add retry logic to API tool</span>
                <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">95% confidence</span>
              </div>
              <div className="bg-black/50 rounded-lg p-4 font-mono text-sm mb-4">
                <div className="text-red-400 mb-2"># Before (fails on timeout)</div>
                <div className="text-gray-400 mb-4">result = tool.call()</div>
                <div className="text-emerald-400 mb-2"># After (with retry logic)</div>
                <div className="text-gray-400">result = tool.call(retries=3, backoff=2)</div>
              </div>
              <div className="flex gap-3">
                <button className="px-4 py-2 bg-emerald-500/20 text-emerald-400 rounded-lg text-sm font-medium">
                  Approve
                </button>
                <button className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg text-sm font-medium">
                  Reject
                </button>
                <button className="px-4 py-2 bg-white/10 text-gray-400 rounded-lg text-sm font-medium">
                  Comment
                </button>
              </div>
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
                { title: 'Timeout Fixes', desc: 'Automatically suggest increased timeouts for slow API calls' },
                { title: 'Schema Mapping', desc: 'Detect field mismatches and suggest schema transformations' },
                { title: 'Retry Logic', desc: 'Recommend retry patterns for flaky external services' },
                { title: 'Error Handling', desc: 'Suggest try/catch blocks for common failure points' }
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
            <h2 className="text-3xl font-medium text-white mb-4">Let AI fix your agent issues</h2>
            <p className="text-gray-400 mb-8">Intelligent corrections that learn from your feedback.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="px-8 py-4 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors inline-flex items-center justify-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/docs#corrective"
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

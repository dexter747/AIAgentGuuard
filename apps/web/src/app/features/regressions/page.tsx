'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { TrendingDown, ArrowRight, Check, Code2, Zap, AlertTriangle } from 'lucide-react'
import { Navbar } from '@/components/Navbar'

export default function RegressionsPage() {
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
              <TrendingDown className="w-8 h-8 text-violet-400" />
            </div>
            <h1 className="text-5xl md:text-6xl font-medium mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Regression Detection
            </h1>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Automatically detect when prompt changes, model updates, or code changes break your agent's behavior.
            </p>
          </motion.div>

          {/* What It Is */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">What is Regression Detection?</h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-6">
              Regression Detection compares your agent's current behavior against baseline executions to identify 
              unintended changes. When you update a prompt, switch from GPT-4 to Claude, or modify tool logic, 
              OverseeX shows you exactly what changed and flags potential regressions before deployment.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { icon: AlertTriangle, title: 'Early Warning', desc: 'Catch breaking changes in dev before they reach production' },
                { icon: Zap, title: 'Automated', desc: 'No manual testing—regressions detected automatically on every run' },
                { icon: Code2, title: 'Detailed Diffs', desc: 'See side-by-side comparisons of outputs, tool calls, and decisions' }
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
                { step: '1', title: 'Establish Baseline', desc: 'Run your agent and mark successful executions as golden baselines' },
                { step: '2', title: 'Make Changes', desc: 'Update prompts, switch models, or modify code as needed' },
                { step: '3', title: 'Detect Regressions', desc: 'OverseeX compares new runs to baselines and flags differences' }
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
                { title: 'Prompt Engineering', desc: 'Safely iterate on prompts without breaking existing functionality' },
                { title: 'Model Migrations', desc: 'Validate GPT-4 to Claude migrations before rolling out' },
                { title: 'Code Refactoring', desc: 'Ensure tool logic changes don\'t alter agent behavior unexpectedly' },
                { title: 'Version Rollback', desc: 'Identify which change caused the regression and roll back safely' }
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
            <h2 className="text-3xl font-medium text-white mb-4">Ready to prevent regressions?</h2>
            <p className="text-gray-400 mb-8">Catch breaking changes before your users do.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="px-8 py-4 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors inline-flex items-center justify-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/docs#regression"
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

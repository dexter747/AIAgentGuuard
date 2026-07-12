'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Boxes, ArrowRight, Check, Code2, Zap, DollarSign } from 'lucide-react'
import { Navbar } from '@/components/Navbar'

export default function MocksPage() {
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
              <Boxes className="w-8 h-8 text-violet-400" />
            </div>
            <h1 className="text-5xl md:text-6xl font-medium mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              API Mocking
            </h1>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Test your AI agents without hitting external APIs—save thousands in API costs while testing faster.
            </p>
          </motion.div>

          {/* What It Is */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-20"
          >
            <h2 className="text-3xl font-medium text-white mb-6">What is API Mocking?</h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-6">
              API Mocking lets you test agents without calling real external services like Stripe, Twilio, SendGrid, 
              or your own APIs. OverseeX intercepts tool calls and returns predefined responses, enabling fast, 
              repeatable testing without API costs, rate limits, or external dependencies.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { icon: DollarSign, title: 'Zero API Costs', desc: 'Test 10,000 times without spending a penny on external APIs' },
                { icon: Zap, title: 'Lightning Fast', desc: 'No network latency—tests run 10x faster with mocked responses' },
                { icon: Code2, title: 'Smart Recording', desc: 'Record real API responses once, replay them infinitely' }
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
                { step: '1', title: 'Record Responses', desc: 'Run your agent once with real APIs—OverseeX captures all responses' },
                { step: '2', title: 'Create Mocks', desc: 'Define mock responses for different scenarios (success, error, timeout)' },
                { step: '3', title: 'Test Infinitely', desc: 'Run tests with mocked APIs as many times as you want—free and fast' }
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
                { title: 'Cost Reduction', desc: 'Test payment agents without charging real credit cards via Stripe' },
                { title: 'Offline Development', desc: 'Work on agents without internet or when external APIs are down' },
                { title: 'Error Scenario Testing', desc: 'Simulate API failures, timeouts, and edge cases easily' },
                { title: 'CI/CD Integration', desc: 'Run tests in CI without exposing production API keys' }
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
            <h2 className="text-3xl font-medium text-white mb-4">Ready to mock your APIs?</h2>
            <p className="text-gray-400 mb-8">Test faster and save thousands on API costs.</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="px-8 py-4 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors inline-flex items-center justify-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/docs#mocks"
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

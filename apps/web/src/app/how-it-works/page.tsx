"use client"

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { Shield, Activity, LineChart, Bell, TestTube, Wrench } from 'lucide-react'
import { Navbar } from '@/components/Navbar'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

export default function HowItWorksPage() {
  const stepsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!stepsRef.current) return

    const ctx = gsap.context(() => {
      const steps = stepsRef.current?.querySelectorAll('.step-card')
      if (steps) {
        gsap.fromTo(
          steps,
          { opacity: 0, y: 50 },
          {
            opacity: 1,
            y: 0,
            duration: 0.8,
            stagger: 0.2,
            scrollTrigger: {
              trigger: stepsRef.current,
              start: 'top 80%',
            },
          }
        )
      }
    })

    return () => ctx.revert()
  }, [])

  const steps = [
    {
      icon: Shield,
      title: '1. Integrate SDK',
      description: 'Add our lightweight SDK to your AI agent application in minutes with just a few lines of code.',
    },
    {
      icon: Activity,
      title: '2. Capture Traces',
      description: 'Automatically capture every interaction, API call, and decision your agents make in real-time.',
    },
    {
      icon: LineChart,
      title: '3. Analyze Performance',
      description: 'View detailed analytics, metrics, and insights about your agent\'s behavior and performance.',
    },
    {
      icon: TestTube,
      title: '4. Auto-Generate Tests',
      description: 'Our AI automatically creates comprehensive test suites based on real production traces.',
    },
    {
      icon: Bell,
      title: '5. Monitor Health',
      description: 'Get real-time alerts for anomalies, regressions, and performance issues before they impact users.',
    },
    {
      icon: Wrench,
      title: '6. Optimize & Iterate',
      description: 'Use insights to improve prompts, optimize workflows, and enhance agent reliability.',
    },
  ]

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      
      <main className="pt-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center py-20">
          <h1 className="text-5xl font-medium mb-6">How OverseeX Works</h1>
          <p className="text-gray-400 text-xl max-w-3xl mx-auto">
            From integration to optimization, here's how OverseeX helps you build reliable AI agents
          </p>
        </div>

        {/* Steps */}
        <div ref={stepsRef} className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 pb-20">
          {steps.map((step, index) => (
            <div
              key={index}
              className="step-card bg-white/5 border border-white/10 rounded-xl p-8 hover:bg-white/10 transition-all"
            >
              <step.icon className="w-12 h-12 text-purple-500 mb-4" />
              <h3 className="text-2xl font-medium mb-3">{step.title}</h3>
              <p className="text-gray-400">{step.description}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center pb-20">
          <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/20 rounded-2xl p-12">
            <h2 className="text-3xl font-medium mb-4">Ready to Get Started?</h2>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Join teams building reliable AI agents with OverseeX
            </p>
            <Link
              href="/signin"
              className="inline-block px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}

"use client"

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import {
  Shield,
  Zap,
  Activity,
  Play,
  Check,
  ArrowRight,
  Code2,
  LineChart,
  GitBranch,
  Lock,
  Sparkles,
  Book,
  Star,
  Github,
  Twitter,
  Linkedin,
  Bot,
  TestTube,
  Bell,
  DollarSign,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  RefreshCw,
  Wrench,
  FileCode,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { CookieConsent } from '@/components/CookieConsent'
import { Navbar } from '@/components/Navbar'
import { BackgroundGradient } from '@/components/BackgroundGradient'
import Stepper, { Step } from '@/components/Stepper'

// Register GSAP plugins
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

// Hero Section
function HeroSection() {
  const headingRef = useRef<HTMLHeadingElement>(null)
  const descRef = useRef<HTMLParagraphElement>(null)
  const benefitsRef = useRef<HTMLDivElement>(null)
  const ctasRef = useRef<HTMLDivElement>(null)
  const badgesRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Set initial state to prevent flash
      gsap.set([headingRef.current, descRef.current], { opacity: 0 })
      if (benefitsRef.current?.children) {
        gsap.set(Array.from(benefitsRef.current.children), { opacity: 0 })
      }
      if (ctasRef.current?.children) {
        gsap.set(Array.from(ctasRef.current.children), { opacity: 0 })
      }
      if (badgesRef.current?.children) {
        gsap.set(Array.from(badgesRef.current.children), { opacity: 0 })
      }
      
      // Create timeline for stagger effect
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
      
      tl.fromTo(headingRef.current,
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, delay: 0.3 }
      )
      .fromTo(descRef.current,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8 },
        '-=0.5'
      )
      .fromTo(benefitsRef.current?.children || [],
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, stagger: 0.1 },
        '-=0.4'
      )
      .fromTo(ctasRef.current?.children || [],
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, stagger: 0.15 },
        '-=0.3'
      )
      .fromTo(badgesRef.current?.children || [],
        { y: 15, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, stagger: 0.1 },
        '-=0.2'
      )
    })

    return () => ctx.revert()
  }, [])

  return (
    <section className="relative z-20 min-h-screen flex items-start pt-32">
      {/* Background */}
      <div className="absolute inset-0 bg-black" />
      
      {/* Hero background image at bottom */}
      <div className="absolute bottom-[-20%] left-0 right-0 h-full">
        <img 
          src="/herobg.avif" 
          alt="Purple Ring" 
          loading="lazy"
          className="block w-full h-full object-cover object-center rotate-180"
        />
      </div>
      
      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {/* Centered Content */}
        <div className="flex flex-col items-center text-center">

          <h1
            ref={headingRef}
            className="text-4xl sm:text-5xl lg:text-6xl font-medium tracking-tight mb-6 leading-[1.1] max-w-4xl text-white"
          >
            Stop Testing <em className="not-italic font-medium">AI Agents</em> Manually
          </h1>

          <p
            ref={descRef}
            className="text-lg mb-8 max-w-2xl text-white/90"
          >
            Ship AI agents with <em>confidence</em>. Auto-generated tests, intelligent mocking, and 24/7 monitoring powered by <em>real production behavior</em>. <span className="font-medium">Cut testing costs by upto 95%</span>
          </p>

          {/* Key benefits */}
          <div
            ref={benefitsRef}
            className="flex flex-wrap items-center justify-center gap-6 mb-8"
          >
            {[
              { icon: TestTube, text: 'Auto-generate tests' },
              { icon: Zap, text: 'Mock APIs, save $$$' },
              { icon: Bell, text: '24/7 monitoring' },
            ].map((item) => (
              <div key={item.text} className="flex items-center gap-2 text-white">
                <item.icon className="w-5 h-5 text-white" />
                <span>{item.text}</span>
              </div>
            ))}
          </div>

          {/* CTAs */}
          <div
            ref={ctasRef}
            className="flex flex-col sm:flex-row gap-4 items-center justify-center"
          >
            <Link
              href="/register"
              className="group px-8 py-4 text-black font-medium rounded-[10px] transition-all shadow-lg flex items-center justify-center gap-2"
              style={{
                backgroundColor: 'rgb(239, 238, 236)',
                border: '0px solid rgba(255, 255, 255, 0.15)'
              }}
            >
              Get Started
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="#how-it-works"
              className="group px-8 py-4 text-white font-medium rounded-[10px] transition-all flex items-center justify-center gap-2"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                border: '0px solid rgba(255, 255, 255, 0.15)'
              }}
            >
              <Play className="w-5 h-5" />
              See How It Works
            </Link>
          </div>

          {/* Trust badges */}
          <div
            ref={badgesRef}
            className="flex items-center gap-6 mt-8 text-sm text-white/60"
          >
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-white" />
              <span>Free tier forever</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-white" />
              <span>Setup in 5 minutes</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-white" />
              <span>No credit card required</span>
            </div>
          </div>

          {/* Social Proof */}
          <div className="flex items-center gap-4 mt-8">
            <div className="flex -space-x-3">
              <img src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop" alt="User" className="w-10 h-10 rounded-full border-2 border-black object-cover" />
              <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop" alt="User" className="w-10 h-10 rounded-full border-2 border-black object-cover" />
              <img src="https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=100&h=100&fit=crop" alt="User" className="w-10 h-10 rounded-full border-2 border-black object-cover" />
              <img src="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&h=100&fit=crop" alt="User" className="w-10 h-10 rounded-full border-2 border-black object-cover" />
              <img src="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&h=100&fit=crop" alt="User" className="w-10 h-10 rounded-full border-2 border-black object-cover" />
            </div>
            <div className="flex flex-col items-start">
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              </div>
              <p className="text-sm text-gray-400 mt-0.5">Trusted by 2,000+ developers</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// Problem Section - Show the pain
function ProblemSection() {
  const sectionRef = useRef<HTMLElement>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)
  const cardsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.set(titleRef.current, { opacity: 0 })
      if (cardsRef.current?.children) {
        gsap.set(Array.from(cardsRef.current.children), { opacity: 0 })
      }
      
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
        }
      })
      
      tl.fromTo(titleRef.current,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, ease: 'power3.out' }
      )
      .fromTo(cardsRef.current?.children || [],
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, stagger: 0.15, ease: 'power3.out' },
        '-=0.4'
      )
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  const problems = [
    {
      icon: DollarSign,
      title: 'Testing Costs Explode',
      description: 'Running 1,000 tests with real APIs costs $500+. Teams either skip testing or burn through budgets.',
      stat: '$0.55',
      statLabel: 'per test with real APIs'
    },
    {
      icon: Clock,
      title: 'Manual Testing Takes Forever',
      description: 'Writing tests for 243 possible execution paths is impossible. Most edge cases never get tested.',
      stat: '10hrs+',
      statLabel: 'to write tests manually'
    },
    {
      icon: AlertTriangle,
      title: 'Bugs Reach Production',
      description: 'Prompt changes silently break agents. Teams discover issues only when customers complain.',
      stat: '60%',
      statLabel: 'of teams ship untested updates'
    },
    {
      icon: XCircle,
      title: 'API Failures Are Silent',
      description: 'When Stripe, OpenAI, or other APIs fail, your agents fail too—without any warning.',
      stat: '2hrs',
      statLabel: 'average time to detect issues'
    },
  ]

  return (
    <section ref={sectionRef} id="problem" className="pb-24 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-black via-red-950/5 to-black" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div ref={titleRef} className="text-center mb-16">
          <div 
            className="inline-flex items-center gap-2 px-4 py-2 rounded-[26px] mb-6"
            style={{
              background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              opacity: 1
            }}
          >
            <AlertTriangle className="w-4 h-4 text-white" />
            <span className="text-sm text-white">The Problem</span>
          </div>
          <h2 
            className="text-3xl sm:text-4xl lg:text-5xl font-medium mb-4"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            AI Agents Are Hard to Test
          </h2>
          <p 
            className="text-lg max-w-2xl mx-auto"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            Traditional testing tools weren&apos;t built for non-deterministic, multi-tool AI agents. Teams struggle with:
          </p>
        </div>

        <div ref={cardsRef} className="grid md:grid-cols-2 gap-6">
          {problems.map((problem, i) => (
            <div
              key={problem.title}
              className="group p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-red-500/30 transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center flex-shrink-0">
                  <problem.icon className="w-6 h-6 text-red-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-medium text-white mb-2">{problem.title}</h3>
                  <p className="text-gray-400 mb-4">{problem.description}</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-medium text-red-400">{problem.stat}</span>
                    <span className="text-sm text-gray-500">{problem.statLabel}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Solution Section - Show the answer
function SolutionSection() {
  const features = [
    {
      badge: 'Feature 1',
      icon: FileCode,
      title: 'Auto-Generate Tests',
      description: 'Connect OverseeX to your agent. It watches real interactions and automatically creates comprehensive test suites. No manual test writing.',
      visual: (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-black/40 border border-white/10 backdrop-blur-sm">
            <code className="text-sm text-emerald-400">
{`# Generated automatically from traces
def test_booking_happy_path():
    result = agent.run("Book meeting")
    assert "scheduled" in result`}
            </code>
          </div>
          <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 to-green-500/10 border border-emerald-500/20">
            <span className="text-white/80 text-sm">Time Saved</span>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              <span className="font-medium text-white text-lg">10hrs → 10min</span>
            </div>
          </div>
        </div>
      ),
      stats: '98% faster test creation'
    },
    {
      badge: 'Feature 2',
      icon: Wrench,
      title: 'Intelligent Mocking',
      description: 'Test without calling Stripe, OpenAI, or other expensive APIs. Smart mocks understand your agent\ ’s context and return realistic, production-like responses.',
      visual: (
        <div className="space-y-3">
          {[
            { name: 'OpenAI API', saved: '$0.03', icon: '🤖' },
            { name: 'Stripe API', saved: '$0.05', icon: '💳' },
            { name: 'SendGrid', saved: '$0.02', icon: '✉️' },
          ].map((api) => (
            <div key={api.name} className="flex items-center justify-between p-4 rounded-xl bg-black/40 border border-white/10 backdrop-blur-sm hover:border-violet-500/30 transition-all">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{api.icon}</span>
                <span className="text-white/90">{api.name}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-emerald-400 font-medium">{api.saved}</span>
                <span className="text-white/60 text-sm">saved/call</span>
              </div>
            </div>
          ))}
          <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-violet-500/10 to-purple-500/10 border border-violet-500/20 text-center">
            <div className="flex items-center justify-center gap-2">
              <DollarSign className="w-5 h-5 text-violet-400" />
              <span className="font-medium text-white text-lg">100x cheaper tests</span>
            </div>
          </div>
        </div>
      ),
      stats: '$10k+ saved monthly'
    },
    {
      badge: 'Feature 3',
      icon: Activity,
      title: '24/7 Monitoring',
      description: 'Continuous health checks monitor your agents every 5 minutes and alert you instantly via Slack or email, before users notice.',
      visual: (
        <div className="space-y-4">
          <div className="p-5 rounded-xl bg-black/40 border border-white/10 backdrop-blur-sm space-y-3">
            {[
              { name: 'Booking Agent', status: 'Healthy', color: 'emerald' },
              { name: 'Payment Agent', status: 'Healthy', color: 'emerald' },
              { name: 'Support Agent', status: 'Slow', color: 'amber' },
            ].map((agent) => (
              <div key={agent.name} className="flex items-center justify-between p-3 rounded-lg bg-black/50">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full bg-${agent.color}-400 animate-pulse`} />
                  <span className="text-white/90">{agent.name}</span>
                </div>
                <span className={`text-xs font-medium px-3 py-1 rounded-full bg-${agent.color}-500/20 text-${agent.color}-400`}>
                  {agent.status}
                </span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-blue-400" />
              <span className="text-white/80 text-sm">Detection Time</span>
            </div>
            <span className="font-medium text-white text-lg">5 minutes</span>
          </div>
        </div>
      ),
      stats: 'Issues caught before users'
    }
  ]

  return (
    <section id="solution" className=" relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-black via-violet-950/10 to-black" />
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 
            className="text-3xl sm:text-4xl lg:text-5xl font-medium mb-4"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            OverseeX Does the Work for You
          </h2>
          <p 
            className="text-lg max-w-2xl mx-auto"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            Three powerful features that transform how you build, test, and monitor AI agents.
          </p>
        </motion.div>

        <div className="space-y-24">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
              className={cn(
                "grid lg:grid-cols-2 gap-12 items-center",
                index % 2 === 1 && "lg:grid-flow-dense"
              )}
            >
              {/* Content Side */}
              <div className={index % 2 === 1 ? "lg:col-start-2" : ""}>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 mb-6">
                  <span className="text-xs font-medium text-white/60">{feature.badge}</span>
                </div>
                
                <div className="flex items-center gap-4 mb-4">
                  <div 
                    className="w-20 h-20 rounded-2xl flex items-center justify-center"
                    style={{
                      backgroundColor: '#7c3aed',
                      boxShadow: '0 0 40px rgba(124, 58, 237, 0.4)'
                    }}
                  >
                    <span className="text-4xl font-medium text-white">0{index + 1}</span>
                  </div>
                  <h3 className="text-3xl font-medium text-white">{feature.title}</h3>
                </div>
                
                <p className="text-lg text-white/70 mb-6 leading-relaxed">
                  {feature.description}
                </p>
                
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20">
                  <Zap className="w-4 h-4 text-violet-400" />
                  <span className="text-sm text-violet-300 font-medium">{feature.stats}</span>
                </div>
              </div>

              {/* Visual Side */}
              <div className={index % 2 === 1 ? "lg:col-start-1 lg:row-start-1" : ""}>
                <div className="relative">
                  {/* Glow effect */}
                  <div className="absolute -inset-4 bg-gradient-to-r from-violet-600/20 to-purple-600/20 rounded-3xl blur-2xl" />
                  
                  <div className="relative p-8 rounded-2xl bg-black/50 border border-white/10 backdrop-blur-sm">
                    {feature.visual}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Features Section
function FeaturesSection() {
  const features = [
    {
      icon: Code2,
      title: "Auto-Generate Tests from Traces",
      description: "Connect Overseex to your agent and it observes real interactions to automatically generate comprehensive test suites, no manual test writing required.",
      color: "violet"
    },
    {
      icon: Zap,
      title: "Intelligent Tool Mocking",
      description: "Mock Stripe, OpenAI, and other APIs without burning tokens. Reduce test costs by 100x.",
      color: "purple"
    },
    {
      icon: Activity,
      title: "Real-time Health Monitoring",
      description: "Proactive health checks for production agents. Get email alerts before your customers notice issues.",
      color: "indigo"
    },
    {
      icon: GitBranch,
      title: "Regression Detection",
      description: "Behavioral fingerprinting catches when prompt changes break your agent. Never deploy broken updates.",
      color: "violet"
    },
    {
      icon: LineChart,
      title: "Cost Analytics",
      description: "Track LLM token usage, API costs, and find optimization opportunities across all your agents.",
      color: "purple"
    },
    {
      icon: Lock,
      title: "Enterprise Security",
      description: "SOC 2 compliant, SSO/SAML support, and on-premise deployment options for sensitive workloads.",
      color: "indigo"
    }
  ]

  return (
    <section id="features" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-medium mb-4">
            <span 
              style={{
                backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}
            >
              Everything you need to ship reliable agents
            </span>
          </h2>
          <p 
            className="text-lg max-w-2xl mx-auto"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            From test generation to production monitoring, OverseeX provides the complete toolkit for AI agent quality.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="group p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-violet-500/50 transition-all hover:shadow-lg hover:shadow-violet-500/10"
            >
              <div className={cn(
                "w-12 h-12 rounded-xl flex items-center justify-center mb-4",
                feature.color === 'violet' ? 'bg-violet-500/20' :
                feature.color === 'purple' ? 'bg-purple-500/20' :
                'bg-indigo-500/20'
              )}>
                <feature.icon className={cn(
                  "w-6 h-6",
                  feature.color === 'violet' ? 'text-violet-400' :
                  feature.color === 'purple' ? 'text-purple-400' :
                  'text-indigo-400'
                )} />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Stats Section
function StatsSection() {
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: '10M+', label: 'Tests Run' },
            { value: '99.9%', label: 'Uptime SLA' },
            { value: '$2.5M', label: 'Customer Savings' },
            { value: '500+', label: 'Teams Trust Us' },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <p 
                className="text-4xl md:text-5xl font-medium mb-2"
                style={{
                  backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}
              >
                {stat.value}
              </p>
              <p className="text-gray-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// How It Works
function HowItWorks() {
  const steps = [
    {
      title: 'Connect Your Agents',
      description: 'Integrate with Langfuse, OpenTelemetry, or our SDK. Start collecting traces in minutes.',
      code: `import { OverseeX } from '@overseex/sdk'

const guard = new OverseeX({
  apiKey: process.env.OVERSEEX_API_KEY
})

// Wrap your agent
const protectedAgent = guard.wrap(myAgent)`
    },
    {
      title: 'Generate Tests Automatically',
      description: 'Our AI analyzes your traces and generates comprehensive test suites covering all execution paths.',
      code: `# Auto-generated test suite
@pytest.mark.overseex
def test_booking_flow():
    with OverseeX.mock_tools():
        result = agent.run("Book meeting")
        assert result.success
        assert mock.called("calendar.create")`
    },
    {
      title: 'Monitor & Get Alerts',
      description: 'Set up health checks for production agents. Get notified via email, Slack, or PagerDuty when issues arise.',
      code: `overseex.register_health_check({
  agent: "payment_agent",
  endpoint: "https://api.example.com/health",
  interval: "5m",
  alerts: ["email", "slack"]
})`
    }
  ]

  return (
    <section id="how-it-works" className="py-24 relative overflow-hidden bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-medium mb-4">
            <span 
              style={{
                backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}
            >
              Get Started In 3 Simple Steps
            </span>
          </h2>
          <p 
            className="text-lg max-w-2xl mx-auto"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            From zero to production monitoring in under 10 minutes.
          </p>
        </motion.div>

        <Stepper
          initialStep={1}
          backButtonText="Previous"
          nextButtonText="Next Step"
        >
          {steps.map((step, index) => (
            <Step key={index}>
              <div className="space-y-6 py-4 px-6">
                <div>
                  <h3 className="text-2xl md:text-3xl font-medium text-white mb-3">{step.title}</h3>
                  <p className="text-gray-400 text-lg">{step.description}</p>
                </div>
                
                <div className="rounded-2xl bg-black border border-white/10 overflow-hidden">
                  <div className="flex items-center gap-2 px-4 py-3 bg-white/5 border-b border-white/10">
                    <div className="w-3 h-3 rounded-full bg-red-500/80" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                    <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  </div>
                  <pre className="p-6 text-sm overflow-x-auto">
                    <code className="text-gray-300">{step.code}</code>
                  </pre>
                </div>
              </div>
            </Step>
          ))}
        </Stepper>
      </div>
    </section>
  )
}

// Pricing Section with Monthly/Annual Toggle
function PricingSection() {
  const [isAnnual, setIsAnnual] = useState(true)
  const sectionRef = useRef<HTMLElement>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)
  const cardsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.set(titleRef.current, { opacity: 0 })
      if (cardsRef.current?.children) {
        gsap.set(Array.from(cardsRef.current.children), { opacity: 0 })
      }
      
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
        }
      })
      
      tl.fromTo(titleRef.current,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, ease: 'power3.out' }
      )
      .fromTo(cardsRef.current?.children || [],
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, stagger: 0.12, ease: 'power3.out' },
        '-=0.4'
      )
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  const plans = [
    {
      name: 'Free (OSS & experiments)',
      monthlyPrice: 0,
      annualPrice: 0,
      description: 'For open source & experimentation',
      features: [
        '50 analyzed traces/month',
        '7-day retention',
        'Basic test generation',
        'Agent graph visualization',
        'Community support',
      ],
      cta: 'Get Started Free',
      popular: false
    },
    {
      name: 'Starter',
      monthlyPrice: 24,
      annualPrice: 19,
      description: 'For individual developers',
      features: [
        '200 analyzed traces/month',
        '14-day retention',
        'Auto test generation',
        'Tool mocking (5 tools)',
        'Agent graph visualization',
        'Regression detection',
        'Basic coordination view',
        'Email support',
      ],
      cta: 'Get Started',
      popular: false
    },
    {
      name: 'Pro',
      monthlyPrice: 99,
      annualPrice: 79,
      description: 'For professional developers',
      features: [
        '1,000 analyzed traces/month',
        '30-day retention',
        'Unlimited test generation',
        'Tool mocking (20 tools)',
        'Coordination analysis',
        'Framework integrations',
        'Corrective suggestions',
        'Health monitoring',
        'Webhooks & alerts',
      ],
      cta: 'Get Started',
      popular: true
    },
    {
      name: 'Team',
      monthlyPrice: 449,
      annualPrice: 349,
      description: 'For teams building agents',
      features: [
        '10,000 traces/month',
        '60-day retention',
        'Everything in Pro',
        'Advanced coordination',
        'Corrective intelligence',
        'Up to 10 team members',
        'Slack & PagerDuty',
        'Priority support',
      ],
      cta: 'Get Started',
      popular: false
    },
    {
      name: 'Enterprise',
      monthlyPrice: null,
      annualPrice: null,
      description: 'For large-scale deployments',
      features: [
        'Unlimited traces',
        '1-year retention',
        'Full corrective AI',
        'Custom AI training',
        'PII auto-redaction',
        'SSO/SAML',
        'On-premise option',
        'Custom integrations',
        'Dedicated support',
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ]

  return (
    <section ref={sectionRef} id="pricing" className="pb-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div ref={titleRef} className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-medium mb-4">
            <span 
              style={{
                backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}
            >
              Simple & Transparent Pricing
            </span>
          </h2>
          <p 
            className="text-lg max-w-2xl mx-auto mb-8"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            Start free, scale as you grow. No hidden fees, no surprises.
          </p>
          <p className="text-gray-400 text-sm">
            Designed for solo builders → production teams → enterprise scale.
          </p>

          {/* Monthly/Annual Toggle */}
          <div className="flex items-center justify-center gap-4">
            <span className={cn(
              "text-sm font-medium transition-colors w-16 text-right",
              !isAnnual ? "text-white" : "text-gray-500"
            )}>
              Monthly
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative w-14 h-7 rounded-full transition-all duration-300 flex-shrink-0"
              style={isAnnual ? {
                background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)'
              } : {
                backgroundColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <motion.div
                animate={{ left: isAnnual ? '32px' : '4px' }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                className="absolute top-1 w-5 h-5 bg-white rounded-full shadow-lg"
              />
            </button>
            <div className="flex items-center gap-2">
              <span className={cn(
                "text-sm font-medium transition-colors w-16",
                isAnnual ? "text-white" : "text-gray-500"
              )}>
                Annual
              </span>
              <span className={cn(
                "px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-medium rounded-full transition-opacity duration-300 whitespace-nowrap",
                isAnnual ? "opacity-100" : "opacity-0"
              )}>
                Save 20%
              </span>
            </div>
          </div>
        </div>

        <div ref={cardsRef} className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
          {plans.map((plan, i) => {
            const price = isAnnual ? plan.annualPrice : plan.monthlyPrice
            
            return (
              <div
                key={plan.name}
                className={cn(
                  "relative p-5 rounded-2xl border transition-all flex flex-col",
                  plan.popular 
                    ? "bg-white/5 hover:border-purple-500/50"
                    : "bg-white/5 border-white/10 hover:border-white/20"
                )}
                style={plan.popular ? {
                  borderColor: 'rgb(128, 89, 227)'
                } : {}}
              >
                {plan.popular && (
                  <div 
                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 text-white text-xs font-medium rounded-full"
                    style={{
                      background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)'
                    }}
                  >
                    Most Popular
                  </div>
                )}
                <h3 className="text-xl font-medium text-white mb-2">{plan.name}</h3>
                <div className="mb-4">
                  {price !== null ? (
                    <>
                      <span className="text-4xl font-medium text-white">${price}</span>
                      <span className="text-gray-400">/month</span>
                      {isAnnual && price > 0 && (
                        <div className="text-xs text-gray-500 mt-1">(billed annually)</div>
                      )}
                    </>
                  ) : (
                    <span className="text-4xl font-medium text-white">Custom</span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mb-6">{plan.description}</p>
                <ul className="space-y-3 mb-8 flex-grow min-h-[180px]">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm text-white">
                      <Check className="w-4 h-4 text-white flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  href={plan.name === 'Enterprise' ? '/contact' : '/register'}
                  className="block w-full py-3 rounded-[10px] font-medium text-center transition-all mt-auto"
                  style={plan.popular ? {
                    background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)',
                    color: 'white'
                  } : {
                    backgroundColor: 'rgba(255, 255, 255, 0.15)',
                    color: 'white'
                  }}
                >
                  {plan.cta}
                </Link>
              </div>
            )
          })}
        </div>

        {/* Secure Payments Badge */}
        <div className="flex justify-center items-center gap-2 mt-12">
          <span className="text-gray-400 text-sm">Secure Payments By</span>
          <img src="/dodo.svg" alt="DODO Payments" className="h-6" />
        </div>
      </div>
    </section>
  )
}

// Testimonials
function TestimonialsSection() {
  const testimonials = [
    {
      quote: "OverseeX reduced our agent testing costs by 95% and caught 3 critical regressions before they hit production. Essential tool for any AI team.",
      author: "Sarah Chen",
      role: "Head of AI",
      company: "TechFlow",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop"
    },
    {
      quote: "The auto-generated tests from traces saved us weeks of manual work. Our deployment confidence went from 60% to 99%.",
      author: "Marcus Johnson",
      role: "Engineering Lead",
      company: "DataPipe",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop"
    },
    {
      quote: "Health monitoring alerts caught an OpenAI API degradation 20 minutes before it affected our users. Game changer.",
      author: "Emily Rodriguez",
      role: "CTO",
      company: "AgentOps",
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop"
    },
    {
      quote: "The tool mocking feature is brilliant. We can test complex agent workflows without hitting external APIs. Saved us thousands in API costs.",
      author: "David Park",
      role: "Senior Developer",
      company: "CloudScale",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop"
    },
    {
      quote: "Integration with our existing observability stack was seamless. OpenTelemetry support made it a breeze to get started.",
      author: "Lisa Wang",
      role: "DevOps Engineer",
      company: "StreamFlow",
      avatar: "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop"
    },
    {
      quote: "We went from manual testing to fully automated test suites in under a week. The trace-based test generation is pure magic.",
      author: "James Mitchell",
      role: "QA Lead",
      company: "TestPro",
      avatar: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop"
    },
    {
      quote: "Finally, a testing platform that understands AI agents. The automatic regression detection has been a lifesaver for our team.",
      author: "Priya Sharma",
      role: "ML Engineer",
      company: "NeuralNet Inc",
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop"
    },
    {
      quote: "Best investment we made this year. The health monitoring alone paid for itself by preventing two major outages.",
      author: "Robert Taylor",
      role: "VP Engineering",
      company: "ScaleAI",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop"
    },
    {
      quote: "The Slack integration keeps our entire team informed about agent health. We catch issues before our users even notice them.",
      author: "Anna Kowalski",
      role: "Product Manager",
      company: "ChatBots Co",
      avatar: "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop"
    },
    {
      quote: "OverseeX gave us the confidence to deploy our agents to production. The comprehensive testing coverage is exactly what we needed.",
      author: "Michael Brown",
      role: "Founder & CEO",
      company: "AgentFirst",
      avatar: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150&h=150&fit=crop"
    }
  ]

  // Duplicate testimonials for infinite scroll effect
  const firstRow = testimonials.slice(0, 5)
  const secondRow = testimonials.slice(5, 10)

  return (
    <section id="testimonials" className="pb-16 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <h2 className="text-4xl md:text-5xl font-medium mb-4">
            <span 
              style={{
                backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}
            >
              Loved By AI Teams
            </span>
          </h2>
          <p 
            className="text-lg max-w-2xl mx-auto"
            style={{
              backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.3) 350%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            See what engineering teams are saying about OverseeX.
          </p>
        </motion.div>
      </div>

      {/* First row - scrolling left */}
      <div className="relative mb-6">
        <div className="flex gap-6 animate-scroll-left">
          {[...firstRow, ...firstRow].map((testimonial, i) => (
            <div
              key={`first-${i}`}
              className="flex-shrink-0 w-[400px] p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm"
            >
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                ))}
              </div>
              <p className="text-gray-300 mb-6 text-sm leading-relaxed">&quot;{testimonial.quote}&quot;</p>
              <div className="flex items-center gap-3">
                <img 
                  src={testimonial.avatar} 
                  alt={testimonial.author}
                  className="w-10 h-10 rounded-full object-cover"
                />
                <div>
                  <p className="font-medium text-white text-sm">{testimonial.author}</p>
                  <p className="text-xs text-gray-400">{testimonial.role}, {testimonial.company}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Second row - scrolling right */}
      <div className="relative">
        <div className="flex gap-6 animate-scroll-right">
          {[...secondRow, ...secondRow].map((testimonial, i) => (
            <div
              key={`second-${i}`}
              className="flex-shrink-0 w-[400px] p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm"
            >
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                ))}
              </div>
              <p className="text-gray-300 mb-6 text-sm leading-relaxed">&quot;{testimonial.quote}&quot;</p>
              <div className="flex items-center gap-3">
                <img 
                  src={testimonial.avatar} 
                  alt={testimonial.author}
                  className="w-10 h-10 rounded-full object-cover"
                />
                <div>
                  <p className="font-medium text-white text-sm">{testimonial.author}</p>
                  <p className="text-xs text-gray-400">{testimonial.role}, {testimonial.company}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// CTA Section
function CTASection() {
  return (
    <section className="pb-16 relative overflow-hidden">
      {/* Purple gradient background */}
      <div className="absolute inset-0 bg-black" />
      
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Dynamic Island Container */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative bg-black rounded-[32px] p-12 md:p-16 shadow-2xl overflow-hidden"
        >          
          <div className="relative z-10 text-center">
            {/* Heading */}
            <h2 className="text-4xl md:text-5xl font-medium mb-6 leading-tight">
              <span 
                style={{
                  backgroundImage: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.7) 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}
              >
                Ready to Ship Reliable AI Agents to Production?
              </span>
            </h2>

            {/* Subheading */}
            <p className="text-lg text-white/80 mb-10 max-w-2xl mx-auto">
              Join hundreds of developers building better AI agents with automated testing and 24/7 monitoring.
            </p>

            {/* CTA Buttons - Same style as Hero */}
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-center mb-8">
              <Link
                href="/register"
                className="group px-8 py-4 text-black font-medium rounded-[10px] transition-all shadow-lg flex items-center justify-center gap-2"
                style={{
                  backgroundColor: 'rgb(239, 238, 236)',
                  border: '0px solid rgba(255, 255, 255, 0.15)'
                }}
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/docs"
                className="group px-8 py-4 text-white font-medium rounded-[10px] transition-all flex items-center justify-center gap-2"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.15)',
                  border: '0px solid rgba(255, 255, 255, 0.15)'
                }}
              >
                <Book className="w-5 h-5" />
                View Documentation
              </Link>
            </div>

            {/* Trust indicators */}
            <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-400" />
                <span>Free 14-day trial</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-400" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-400" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </div>

          {/* Decorative corner accents */}
          <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-violet-600/20 to-transparent rounded-tl-[32px]" />
          <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tl from-purple-600/20 to-transparent rounded-br-[32px]" />
        </motion.div>
      </div>

      {/* Decorative blur elements */}
      <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px] -translate-y-1/2" />
      <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-[120px] -translate-y-1/2" />
    </section>
  )
}

// Footer
function Footer() {
  return (
    <footer className="py-16 border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 mb-12">
          {/* Brand */}
          <div className="col-span-2">
            <Link href="/" className="flex items-center gap-3 mb-4">
              <img 
                src="/logo.jpeg" 
                alt="OverseeX" 
                className="h-10 w-auto"
              />
              <span className="text-3xl font-medium text-white">OverseeX</span>
            </Link>
            <p className="text-gray-400 text-sm mb-4 max-w-xs">
              The complete testing & monitoring platform for AI agents.
            </p>
            <div className="flex items-center gap-4">
              <a href="https://github.com/overseex" className="text-gray-400 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="https://twitter.com/overseex" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="https://linkedin.com/company/overseex" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-medium text-white mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="#solution" className="text-gray-400 hover:text-white transition-colors">Features</Link></li>
              <li><Link href="#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</Link></li>
              <li><Link href="/docs" className="text-gray-400 hover:text-white transition-colors">Documentation</Link></li>
              <li><Link href="/changelog" className="text-gray-400 hover:text-white transition-colors">Changelog</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-medium text-white mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/about" className="text-gray-400 hover:text-white transition-colors">About</Link></li>
              <li><Link href="/blog" className="text-gray-400 hover:text-white transition-colors">Blog</Link></li>
              <li><Link href="/careers" className="text-gray-400 hover:text-white transition-colors">Careers</Link></li>
              <li><Link href="/contact" className="text-gray-400 hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-medium text-white mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</Link></li>
              <li><Link href="/terms" className="text-gray-400 hover:text-white transition-colors">Terms of Service</Link></li>
              <li><Link href="/cookies" className="text-gray-400 hover:text-white transition-colors">Cookie Policy</Link></li>
              <li><Link href="/refund" className="text-gray-400 hover:text-white transition-colors">Refund Policy</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="font-medium text-white mb-4">Support</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/docs" className="text-gray-400 hover:text-white transition-colors">Help Center</Link></li>
              <li><Link href="/status" className="text-gray-400 hover:text-white transition-colors">Status Page</Link></li>
              <li><Link href="/shipping" className="text-gray-400 hover:text-white transition-colors">Delivery Policy</Link></li>
              <li><a href="mailto:support@overseex.com" className="text-gray-400 hover:text-white transition-colors">Contact Support</a></li>
            </ul>
          </div>
        </div>

        {/* Payment & Developer Badges */}
        <div className="pt-8 border-t border-white/10 flex flex-wrap items-center justify-center gap-8 mb-4">
          <div className="flex items-center gap-2">
            <span className="text-white text-sm">Secure Payments By</span>
            <img src="/dodo.svg" alt="DODO Payments" className="h-5" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-white text-sm">Developed & Maintained By</span>
            <img src="/nexolve-comp.svg" alt="Nexolve Technologies" className="h-5" />
            <a href="https://nexolve.tech" target="_blank" rel="noopener noreferrer" className="text-white hover:text-blue-500 transition-colors text-sm">Nexolve Technologies</a>
          </div>
        </div>

        <div className="pt-4 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-500">© 2026 OverseeX. All rights reserved.</p>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            All systems operational
          </div>
        </div>
      </div>
    </footer>
  )
}

// Main Page
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black text-foreground relative">
      <Navbar />
      <main>
        <HeroSection />
        <BackgroundGradient />
        <SolutionSection />
        <HowItWorks />
        <PricingSection />
        {/* <TestimonialsSection /> */}
        <CTASection />
      </main>
      <Footer />
      <CookieConsent />
    </div>
  )
}

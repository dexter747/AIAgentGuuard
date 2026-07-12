'use client'

import { DollarSign, Clock, TrendingDown, AlertTriangle, XCircle, Zap } from 'lucide-react'

export function BackgroundGradient() {
  const challenges = [
    {
      icon: DollarSign,
      title: 'Testing Costs Explode',
      value: '$500+',
      description: 'Cost per 1,000 test runs using real APIs'
    },
    {
      icon: Clock,
      title: 'Manual Testing Takes Forever',
      value: '10+ hrs',
      description: 'Writing tests for complex agents manually'
    },
    {
      icon: TrendingDown,
      title: 'Teams Skip Testing',
      value: '60%',
      description: 'Teams ship untested updates due to testing complexity'
    },
    {
      icon: AlertTriangle,
      title: 'Bugs Reach Production',
      value: '2-3 days',
      description: 'Average time to detect issues in production'
    },
    {
      icon: XCircle,
      title: 'API Failures Are Silent',
      value: '2 hrs',
      description: 'Average time to detect API failures'
    },
    {
      icon: Zap,
      title: 'Edge Cases Untested',
      value: '243+',
      description: 'Possible execution paths never tested'
    },
  ]

  return (
    <section className="relative z-10 pt-40 pb-24 overflow-hidden bg-black">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 
            className="text-3xl sm:text-4xl lg:text-5xl font-medium mb-6"
            style={{
              background: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.5) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            AI Agents Are Hard to Test
          </h2>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto">
            Traditional testing tools weren't built for non-deterministic AI behavior. Teams struggle with these critical challenges.
          </p>
        </div>

        {/* 3x2 Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {challenges.map((challenge, index) => (
            <div
              key={index}
              className="group relative p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm hover:border-purple-500 hover:shadow-[0_0_30px_rgba(168,85,247,0.4)] transition-all duration-300"
            >
              <div 
                className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"
                style={{
                  background: 'linear-gradient(135deg, rgba(79, 26, 214, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)'
                }}
              />
              <div className="relative">
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                  style={{
                    background: 'linear-gradient(135deg, rgba(79, 26, 214, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)'
                  }}
                >
                  <challenge.icon className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-medium text-white mb-3">{challenge.title}</h3>
                <div className="text-3xl font-medium text-purple-400 mb-2">{challenge.value}</div>
                <p className="text-sm text-gray-400">{challenge.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

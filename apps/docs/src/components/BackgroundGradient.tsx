'use client'

import { AlertTriangle, TrendingDown, Clock, DollarSign } from 'lucide-react'

export function BackgroundGradient() {
  const stats = [
    {
      icon: DollarSign,
      value: '$500+',
      label: 'Cost per 1,000 tests',
      subtext: 'with real APIs'
    },
    {
      icon: Clock,
      value: '10+ hrs',
      label: 'Manual test writing',
      subtext: 'for complex agents'
    },
    {
      icon: TrendingDown,
      value: '60%',
      label: 'Teams skip testing',
      subtext: 'due to complexity'
    },
    {
      icon: AlertTriangle,
      value: '2-3 days',
      label: 'To detect bugs',
      subtext: 'in production'
    },
  ]

  return (
    <section className="relative py-24 overflow-hidden">
      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div 
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6 border"
            style={{
              background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)',
              borderColor: 'rgba(255, 255, 255, 0.1)'
            }}
          >
            <AlertTriangle className="w-4 h-4 text-white" />
            <span className="text-sm text-white font-medium">The Testing Crisis</span>
          </div>
          <h2 
            className="text-3xl sm:text-4xl lg:text-5xl font-medium mb-6"
            style={{
              background: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.5) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            AI Agents Are Breaking in Production
          </h2>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto">
            Traditional testing tools can't keep up with non-deterministic AI behavior. Teams are either burning budgets or shipping broken agents.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="group relative p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300"
            >
              <div 
                className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"
                style={{
                  background: 'linear-gradient(135deg, rgba(79, 26, 214, 0.05) 0%, rgba(128, 89, 227, 0.05) 100%)'
                }}
              />
              <div className="relative">
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                  style={{
                    background: 'linear-gradient(135deg, rgba(79, 26, 214, 0.15) 0%, rgba(128, 89, 227, 0.15) 100%)'
                  }}
                >
                  <stat.icon className="w-6 h-6 text-purple-400" />
                </div>
                <div className="text-3xl font-medium text-white mb-2">{stat.value}</div>
                <div className="text-sm font-medium text-gray-300 mb-1">{stat.label}</div>
                <div className="text-xs text-gray-500">{stat.subtext}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-12 text-center">
          <p className="text-gray-400">
            Without proper testing, <span className="text-purple-400 font-medium">your next deployment could be a disaster</span>
          </p>
        </div>
      </div>
    </section>
  )
}

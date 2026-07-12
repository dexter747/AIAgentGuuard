'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Menu, X, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [featuresOpen, setFeaturesOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const features = [
    { name: 'Traces', href: '/features/traces' },
    { name: 'Agents', href: '/features/agents' },
    { name: 'Agent Graph', href: '/features/agent-graph' },
    { name: 'Coordination', href: '/features/coordination' },
    { name: 'Auto Test Generation', href: '/features/tests' },
    { name: 'Health Monitoring', href: '/features/health' },
    { name: 'API Mocking', href: '/features/mocks' },
    { name: 'Regressions', href: '/features/regressions' },
    { name: 'AI Insights', href: '/features/insights' },
    { name: 'Corrective Intelligence', href: '/features/corrective' },
    { name: 'Framework Integrations', href: '/features/integrations' },
    { name: 'Webhooks', href: '/features/webhooks' },
  ]

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        isScrolled 
          ? "bg-black/80 backdrop-blur-xl border-b border-white/10 shadow-lg" 
          : "bg-black/40 backdrop-blur-md border-b border-white/5"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 flex-shrink-0">
            <img 
              src="/logo.jpeg" 
              alt="OverseeX" 
              className="h-10 w-auto"
            />
            <span className="text-3xl font-medium text-white">OverseeX</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8 flex-1 justify-center">
            {/* Features Dropdown */}
            <div 
              className="relative"
              onMouseEnter={() => setFeaturesOpen(true)}
              onMouseLeave={() => setFeaturesOpen(false)}
            >
              <button className="flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors">
                Features
                <ChevronDown className="w-4 h-4" />
              </button>
              <AnimatePresence>
                {featuresOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute top-full left-0 mt-2 w-[380px] bg-black/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-xl overflow-hidden p-3"
                  >
                    <div className="grid grid-cols-2 gap-1">
                      {features.map((feature) => (
                        <Link
                          key={feature.name}
                          href={feature.href}
                          className="block px-4 py-3 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors rounded-lg"
                        >
                          {feature.name}
                        </Link>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <Link href="/utility" className="text-sm text-gray-400 hover:text-white transition-colors">Utility</Link>
            <Link href="/how-it-works" className="text-sm text-gray-400 hover:text-white transition-colors">How It Works</Link>
            <Link href="/pricing" className="text-sm text-gray-400 hover:text-white transition-colors">Pricing</Link>
            <Link href="/blog" className="text-sm text-gray-400 hover:text-white transition-colors">Blog</Link>
            <Link href="/contact" className="text-sm text-gray-400 hover:text-white transition-colors">Contact</Link>
            <a href="https://docs.overseex.com" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-400 hover:text-white transition-colors">Docs</a>
          </div>

          {/* CTA */}
          <div className="hidden md:flex items-center flex-shrink-0">
            <Link
              href="/signin"
              className="px-4 py-2 text-black text-sm font-medium rounded-[10px] transition-all"
              style={{
                backgroundColor: 'rgb(239, 238, 236)'
              }}
            >
              Sign In
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 text-gray-400"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden py-4 border-t border-white/10"
          >
            <div className="flex flex-col gap-4">
              <div>
                <div className="text-gray-500 text-xs font-medium px-4 py-2">Features</div>
                {features.map((feature) => (
                  <Link key={feature.name} href={feature.href} className="text-gray-400 hover:text-white px-4 py-2 block text-sm">
                    {feature.name}
                  </Link>
                ))}
              </div>
              <Link href="/utility" className="text-gray-400 hover:text-white px-4 py-2">Utility</Link>
              <Link href="/how-it-works" className="text-gray-400 hover:text-white px-4 py-2">How It Works</Link>
              <Link href="/pricing" className="text-gray-400 hover:text-white px-4 py-2">Pricing</Link>
              <Link href="/blog" className="text-gray-400 hover:text-white px-4 py-2">Blog</Link>
              <Link href="/contact" className="text-gray-400 hover:text-white px-4 py-2">Contact</Link>
              <a href="https://docs.overseex.com" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white px-4 py-2">Docs</a>
              <div className="border-t border-white/10 my-2" />
              <Link
                href="/signin"
                className="mx-2 px-4 py-2 text-black text-sm font-medium rounded-[10px] text-center"
                style={{
                  backgroundColor: 'rgb(239, 238, 236)'
                }}
              >
                Sign In
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  )
}

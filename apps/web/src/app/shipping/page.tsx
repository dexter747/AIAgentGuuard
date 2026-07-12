"use client"

import Link from 'next/link'
import { Shield, ArrowLeft, Cloud, Globe, Zap } from 'lucide-react'

export default function ShippingPolicyPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/10">
        <div className="max-w-4xl mx-auto px-4 py-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-medium">OverseeX</span>
          </Link>
          <Link href="/" className="text-gray-400 hover:text-white transition-colors flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-medium mb-4">Delivery & Access Policy</h1>
        <p className="text-gray-400 mb-12">Last updated: January 24, 2026</p>

        {/* Key Message */}
        <div className="p-6 rounded-2xl bg-violet-500/10 border border-violet-500/30 mb-12">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center flex-shrink-0">
              <Cloud className="w-6 h-6 text-violet-400" />
            </div>
            <div>
              <h2 className="text-xl font-medium text-white mb-2">Digital Service - Instant Access</h2>
              <p className="text-gray-300">
                OverseeX is a cloud-based Software as a Service (SaaS) platform. There is no physical shipping involved. Access to our platform is delivered instantly and digitally.
              </p>
            </div>
          </div>
        </div>

        <div className="prose prose-invert prose-violet max-w-none">
          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">1. Service Delivery</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              OverseeX is a digital platform accessible via the internet. Upon registration and payment (for paid plans), you receive:
            </p>
            
            <div className="grid gap-4">
              <div className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
                <Zap className="w-5 h-5 text-violet-400 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-white mb-1">Instant Platform Access</h3>
                  <p className="text-gray-400 text-sm">
                    Immediately after account creation or subscription activation, you can access all features included in your plan at <a href="https://app.overseex.com" className="text-violet-400 hover:underline">app.overseex.com</a>
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
                <Globe className="w-5 h-5 text-violet-400 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-white mb-1">Global Availability</h3>
                  <p className="text-gray-400 text-sm">
                    Our service is available worldwide, 24/7. No geographic restrictions apply (subject to export control regulations).
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
                <Cloud className="w-5 h-5 text-violet-400 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-white mb-1">API Keys & SDK Access</h3>
                  <p className="text-gray-400 text-sm">
                    Your API keys are generated instantly and available in your dashboard. SDKs can be downloaded from npm (JavaScript) or PyPI (Python).
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">2. No Physical Shipping</h2>
            <p className="text-gray-300 leading-relaxed">
              As a purely digital service, OverseeX does not involve:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2 mt-4">
              <li>Physical product shipments</li>
              <li>Delivery tracking numbers</li>
              <li>Shipping addresses or fees</li>
              <li>Customs or import duties</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">3. Access Requirements</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              To use OverseeX, you need:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>A modern web browser (Chrome, Firefox, Safari, or Edge - latest 2 versions)</li>
              <li>An active internet connection</li>
              <li>A valid email address for account verification</li>
              <li>For SDK integration: Node.js 18+ or Python 3.9+</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">4. Subscription Activation Timeline</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 text-gray-400">Plan Type</th>
                    <th className="text-left py-3 text-gray-400">Activation Time</th>
                    <th className="text-left py-3 text-gray-400">Access Level</th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  <tr className="border-b border-white/5">
                    <td className="py-3">Free Tier</td>
                    <td className="py-3">Instant (upon email verification)</td>
                    <td className="py-3">Full free features</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="py-3">Free Trial</td>
                    <td className="py-3">Instant (no payment required)</td>
                    <td className="py-3">Full paid features for 14 days</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="py-3">Paid Plans</td>
                    <td className="py-3">Instant (upon payment confirmation)</td>
                    <td className="py-3">All features for your tier</td>
                  </tr>
                  <tr>
                    <td className="py-3">Enterprise</td>
                    <td className="py-3">Within 24-48 hours (after contract signing)</td>
                    <td className="py-3">Custom configuration</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">5. Service Level Agreement (SLA)</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              We strive for high availability:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li><strong>Free & Starter:</strong> Best-effort availability</li>
              <li><strong>Pro & Team:</strong> 99.5% uptime target</li>
              <li><strong>Enterprise:</strong> 99.9% SLA with service credits</li>
            </ul>
            <p className="text-gray-300 mt-4">
              Current status is always available at <a href="https://status.overseex.com" className="text-violet-400 hover:underline">status.overseex.com</a>
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">6. Data Centers & Regions</h2>
            <p className="text-gray-300 leading-relaxed">
              OverseeX operates from the following regions:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2 mt-4">
              <li><strong>Primary:</strong> United States (US-East)</li>
              <li><strong>Secondary:</strong> Europe (EU-West)</li>
              <li><strong>Enterprise:</strong> Custom region deployment available</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">7. Access Issues</h2>
            <p className="text-gray-300 leading-relaxed">
              If you experience issues accessing the platform after subscription:
            </p>
            <ol className="list-decimal list-inside text-gray-300 space-y-2 mt-4">
              <li>Check our status page for any ongoing incidents</li>
              <li>Clear your browser cache and cookies</li>
              <li>Try a different browser or incognito mode</li>
              <li>Contact support at <a href="mailto:support@overseex.com" className="text-violet-400 hover:underline">support@overseex.com</a></li>
            </ol>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">8. Contact</h2>
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <p className="text-gray-300">
                <strong className="text-white">Customer Support</strong><br />
                Email: <a href="mailto:support@overseex.com" className="text-violet-400 hover:underline">support@overseex.com</a><br />
                Response time: Within 24 hours (business days)
              </p>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="max-w-4xl mx-auto px-4 flex flex-wrap items-center justify-between gap-4">
          <p className="text-sm text-gray-500">© 2026 OverseeX. All rights reserved.</p>
          <div className="flex items-center gap-6 text-sm">
            <Link href="/terms" className="text-gray-400 hover:text-white transition-colors">Terms</Link>
            <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">Privacy</Link>
            <Link href="/cookies" className="text-gray-400 hover:text-white transition-colors">Cookies</Link>
            <Link href="/refund" className="text-gray-400 hover:text-white transition-colors">Refund</Link>
            <Link href="/shipping" className="text-violet-400">Delivery</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

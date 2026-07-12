"use client"

import Link from 'next/link'
import { Shield, ArrowLeft, XCircle, Check } from 'lucide-react'

export default function RefundPolicyPage() {
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
        <h1 className="text-4xl font-medium mb-4">Refund Policy</h1>
        <p className="text-gray-400 mb-12">Last updated: January 24, 2026</p>

        {/* Key Message */}
        <div className="p-6 rounded-2xl bg-violet-500/10 border border-violet-500/30 mb-12">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center flex-shrink-0">
              <XCircle className="w-6 h-6 text-violet-400" />
            </div>
            <div>
              <h2 className="text-xl font-medium text-white mb-2">No Refunds Policy</h2>
              <p className="text-gray-300">
                OverseeX operates a <strong>no refunds policy</strong> for all paid subscriptions. We offer a generous free tier so you can thoroughly evaluate our platform before committing to a paid plan.
              </p>
            </div>
          </div>
        </div>

        <div className="prose prose-invert prose-violet max-w-none">
          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">Why No Refunds?</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              We believe in transparency and giving you every opportunity to evaluate OverseeX before you pay:
            </p>
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" />
                <div>
                  <strong className="text-white">Free Tier Available:</strong>
                  <span className="text-gray-300"> Our free plan includes 50 analyzed traces/month, allowing you to fully test our core features before upgrading.</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" />
                <div>
                  <strong className="text-white">14-Day Free Trial:</strong>
                  <span className="text-gray-300"> All paid plans include a 14-day free trial with full feature access—no credit card required to start.</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" />
                <div>
                  <strong className="text-white">Cancel Anytime:</strong>
                  <span className="text-gray-300"> You can cancel your subscription at any time. Your access continues until the end of your billing period.</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" />
                <div>
                  <strong className="text-white">Transparent Pricing:</strong>
                  <span className="text-gray-300"> No hidden fees or surprise charges. What you see is what you pay.</span>
                </div>
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">What This Means for You</h2>
            
            <div className="grid gap-4">
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="font-medium text-white mb-2">Monthly Subscriptions</h3>
                <p className="text-gray-300 text-sm">
                  If you cancel, your subscription remains active until the end of your current billing month. No partial refunds are provided for unused days.
                </p>
              </div>
              
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="font-medium text-white mb-2">Annual Subscriptions</h3>
                <p className="text-gray-300 text-sm">
                  Annual plans are charged upfront for the full year. If you cancel, you retain access until your annual term ends. No partial or prorated refunds.
                </p>
              </div>
              
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="font-medium text-white mb-2">Plan Changes</h3>
                <p className="text-gray-300 text-sm">
                  You can upgrade or downgrade your plan at any time. Upgrades are prorated and take effect immediately. Downgrades take effect at the next billing cycle.
                </p>
              </div>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">Exceptions</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              In rare circumstances, we may consider exceptions on a case-by-case basis:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Duplicate charges due to technical errors</li>
              <li>Fraudulent transactions (reported within 48 hours)</li>
              <li>Service unavailability exceeding 72 consecutive hours (Enterprise SLA customers only)</li>
            </ul>
            <p className="text-gray-300 mt-4">
              To request an exception review, contact us at <a href="mailto:billing@overseex.com" className="text-violet-400 hover:underline">billing@overseex.com</a> within 7 days of the charge.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">How to Cancel</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              You can cancel your subscription at any time:
            </p>
            <ol className="list-decimal list-inside text-gray-300 space-y-2">
              <li>Log in to your OverseeX account</li>
              <li>Go to <strong>Settings → Billing</strong></li>
              <li>Click <strong>Cancel Subscription</strong></li>
              <li>Confirm your cancellation</li>
            </ol>
            <p className="text-gray-300 mt-4">
              You will receive a confirmation email. Your access continues until your current billing period ends.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">Digital Services Disclaimer</h2>
            <p className="text-gray-300 leading-relaxed">
              OverseeX is a digital service, not a physical product. As such, standard return policies do not apply. Once you subscribe and gain access to premium features, the service is considered delivered.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">Questions?</h2>
            <p className="text-gray-300 leading-relaxed">
              If you have questions about our refund policy or need assistance:
            </p>
            <div className="mt-4 p-6 rounded-xl bg-white/5 border border-white/10">
              <p className="text-gray-300">
                <strong className="text-white">Billing Support</strong><br />
                Email: <a href="mailto:billing@overseex.com" className="text-violet-400 hover:underline">billing@overseex.com</a><br />
                Response time: Within 24 hours
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
            <Link href="/refund" className="text-violet-400">Refund Policy</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

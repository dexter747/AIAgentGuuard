"use client"

import Link from 'next/link'
import { Shield, ArrowLeft } from 'lucide-react'

export default function TermsOfServicePage() {
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
        <h1 className="text-4xl font-medium mb-4">Terms of Service</h1>
        <p className="text-gray-400 mb-12">Last updated: January 24, 2026</p>

        <div className="prose prose-invert prose-violet max-w-none">
          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-300 leading-relaxed">
              By accessing or using OverseeX (&quot;Service&quot;), you agree to be bound by these Terms of Service (&quot;Terms&quot;). If you do not agree to these Terms, do not use our Service. These Terms apply to all users, including organizations and their team members.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">2. Description of Service</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              OverseeX is a testing and monitoring platform for AI agents. Our Service includes:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Automated test generation from agent execution traces</li>
              <li>Intelligent tool mocking for cost-effective testing</li>
              <li>Health monitoring and alerting for production agents</li>
              <li>Analytics and performance tracking</li>
              <li>APIs and SDKs for integration</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">3. Account Registration</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              To use OverseeX, you must create an account. You agree to:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Provide accurate, current, and complete information</li>
              <li>Maintain and update your information as needed</li>
              <li>Keep your password secure and confidential</li>
              <li>Accept responsibility for all activity under your account</li>
              <li>Notify us immediately of any unauthorized access</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">4. Subscription Plans and Billing</h2>
            
            <h3 className="text-xl font-medium text-white mb-3">4.1 Pricing</h3>
            <p className="text-gray-300 leading-relaxed mb-4">
              We offer various subscription plans with different features and limits. Prices are as displayed on our pricing page and may change with 30 days&apos; notice for existing subscribers.
            </p>

            <h3 className="text-xl font-medium text-white mb-3">4.2 Payment</h3>
            <p className="text-gray-300 leading-relaxed mb-4">
              Paid subscriptions are billed in advance on a monthly or annual basis. You authorize us to charge your payment method for all fees incurred. Failure to pay may result in suspension or termination of your account.
            </p>

            <h3 className="text-xl font-medium text-white mb-3">4.3 Free Trial</h3>
            <p className="text-gray-300 leading-relaxed">
              We may offer free trials. At the end of the trial, you will be charged unless you cancel before the trial ends.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">5. Acceptable Use</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              You agree NOT to use OverseeX to:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Violate any laws or regulations</li>
              <li>Infringe on intellectual property rights</li>
              <li>Transmit harmful code, viruses, or malware</li>
              <li>Attempt unauthorized access to our systems</li>
              <li>Interfere with or disrupt the Service</li>
              <li>Resell or redistribute the Service without authorization</li>
              <li>Use the Service for competitive analysis without permission</li>
              <li>Exceed rate limits or abuse API access</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">6. Intellectual Property</h2>
            
            <h3 className="text-xl font-medium text-white mb-3">6.1 Our Rights</h3>
            <p className="text-gray-300 leading-relaxed mb-4">
              OverseeX, its features, and all related content are owned by us and protected by intellectual property laws. You may not copy, modify, or create derivative works without permission.
            </p>

            <h3 className="text-xl font-medium text-white mb-3">6.2 Your Data</h3>
            <p className="text-gray-300 leading-relaxed">
              You retain ownership of all data you submit to OverseeX. You grant us a limited license to use this data solely to provide and improve the Service.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">7. Confidentiality</h2>
            <p className="text-gray-300 leading-relaxed">
              We treat your agent configurations, traces, and test data as confidential. We will not share this information except as described in our Privacy Policy or with your explicit consent.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">8. Service Availability</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              We strive for high availability but do not guarantee uninterrupted service. We may:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Perform scheduled maintenance with advance notice</li>
              <li>Modify or discontinue features with reasonable notice</li>
              <li>Experience occasional downtime due to circumstances beyond our control</li>
            </ul>
            <p className="text-gray-300 mt-4">
              Enterprise customers may have specific SLA terms in their agreements.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">9. Disclaimer of Warranties</h2>
            <p className="text-gray-300 leading-relaxed">
              THE SERVICE IS PROVIDED &quot;AS IS&quot; WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICE WILL BE ERROR-FREE OR UNINTERRUPTED.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">10. Limitation of Liability</h2>
            <p className="text-gray-300 leading-relaxed">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, OVERSEEX SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY. OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT PAID BY YOU IN THE 12 MONTHS PRECEDING THE CLAIM.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">11. Indemnification</h2>
            <p className="text-gray-300 leading-relaxed">
              You agree to indemnify and hold harmless OverseeX and its officers, directors, employees, and agents from any claims, damages, or expenses arising from your use of the Service, violation of these Terms, or infringement of any third-party rights.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">12. Termination</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              Either party may terminate this agreement:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>You may cancel your subscription at any time through your account settings</li>
              <li>We may suspend or terminate accounts that violate these Terms</li>
              <li>We may terminate with 30 days&apos; notice for any reason</li>
            </ul>
            <p className="text-gray-300 mt-4">
              Upon termination, your right to use the Service ceases. We may retain your data as required by law or for legitimate business purposes.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">13. Governing Law</h2>
            <p className="text-gray-300 leading-relaxed">
              These Terms shall be governed by the laws of the State of Delaware, USA, without regard to conflict of law principles. Any disputes shall be resolved in the courts of Delaware.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">14. Changes to Terms</h2>
            <p className="text-gray-300 leading-relaxed">
              We may modify these Terms at any time. We will notify you of material changes via email or platform notification. Continued use after changes constitutes acceptance of the new Terms.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">15. Contact Information</h2>
            <p className="text-gray-300 leading-relaxed">
              For questions about these Terms:
            </p>
            <div className="mt-4 p-6 rounded-xl bg-white/5 border border-white/10">
              <p className="text-gray-300">
                <strong className="text-white">OverseeX Legal</strong><br />
                Email: <a href="mailto:legal@overseex.com" className="text-violet-400 hover:underline">legal@overseex.com</a>
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
            <Link href="/terms" className="text-violet-400">Terms</Link>
            <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">Privacy</Link>
            <Link href="/cookies" className="text-gray-400 hover:text-white transition-colors">Cookies</Link>
            <Link href="/refund" className="text-gray-400 hover:text-white transition-colors">Refund Policy</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

"use client"

import Link from 'next/link'
import { Shield, ArrowLeft } from 'lucide-react'

export default function PrivacyPolicyPage() {
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
        <h1 className="text-4xl font-medium mb-4">Privacy Policy</h1>
        <p className="text-gray-400 mb-12">Last updated: January 24, 2026</p>

        <div className="prose prose-invert prose-violet max-w-none">
          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">1. Introduction</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              OverseeX (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI agent testing and monitoring platform.
            </p>
            <p className="text-gray-300 leading-relaxed">
              We comply with the General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), and other applicable data protection laws. By using OverseeX, you consent to the data practices described in this policy.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">2. Information We Collect</h2>
            
            <h3 className="text-xl font-medium text-white mb-3">2.1 Information You Provide</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-2 mb-4">
              <li><strong>Account Information:</strong> Name, email address, password, company name</li>
              <li><strong>Billing Information:</strong> Payment method details, billing address (processed by our payment provider)</li>
              <li><strong>Agent Data:</strong> AI agent configurations, traces, test results, and monitoring data you submit</li>
              <li><strong>Communications:</strong> Support tickets, feedback, and correspondence with us</li>
            </ul>

            <h3 className="text-xl font-medium text-white mb-3">2.2 Information Collected Automatically</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li><strong>Usage Data:</strong> Features used, actions taken, time spent on platform</li>
              <li><strong>Device Information:</strong> Browser type, operating system, IP address</li>
              <li><strong>Cookies:</strong> Session identifiers, preferences (see our Cookie Policy)</li>
              <li><strong>Log Data:</strong> Server logs, error reports, performance metrics</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-300 mb-4">We use collected information for:</p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li>Providing and maintaining the OverseeX platform</li>
              <li>Processing transactions and sending billing-related communications</li>
              <li>Sending technical notices, security alerts, and support messages</li>
              <li>Responding to your comments and questions</li>
              <li>Analyzing usage patterns to improve our services</li>
              <li>Detecting and preventing fraud and abuse</li>
              <li>Complying with legal obligations</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">4. Data Sharing and Disclosure</h2>
            <p className="text-gray-300 mb-4">We do not sell your personal information. We may share data with:</p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li><strong>Service Providers:</strong> Payment processors, cloud hosting, email services (under strict data processing agreements)</li>
              <li><strong>Legal Requirements:</strong> When required by law, court order, or government request</li>
              <li><strong>Business Transfers:</strong> In connection with mergers, acquisitions, or asset sales</li>
              <li><strong>With Consent:</strong> When you explicitly authorize sharing</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">5. Your Rights (GDPR & CCPA)</h2>
            <p className="text-gray-300 mb-4">You have the right to:</p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Rectification:</strong> Correct inaccurate or incomplete data</li>
              <li><strong>Erasure:</strong> Request deletion of your personal data (&quot;right to be forgotten&quot;)</li>
              <li><strong>Portability:</strong> Receive your data in a machine-readable format</li>
              <li><strong>Restriction:</strong> Limit how we process your data</li>
              <li><strong>Objection:</strong> Object to certain processing activities</li>
              <li><strong>Withdraw Consent:</strong> Revoke previously given consent</li>
            </ul>
            <p className="text-gray-300 mt-4">
              To exercise these rights, email us at <a href="mailto:privacy@overseex.com" className="text-violet-400 hover:underline">privacy@overseex.com</a> or use the Data Control settings in your account.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">6. Data Security</h2>
            <p className="text-gray-300 leading-relaxed">
              We implement industry-standard security measures including:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2 mt-4">
              <li>TLS 1.3 encryption for all data in transit</li>
              <li>AES-256 encryption for data at rest</li>
              <li>Regular security audits and penetration testing</li>
              <li>SOC 2 Type II compliance (Enterprise tier)</li>
              <li>Multi-factor authentication support</li>
              <li>Role-based access controls</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">7. Data Retention</h2>
            <p className="text-gray-300 leading-relaxed">
              We retain your data for as long as your account is active or as needed to provide services. Retention periods vary by plan:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2 mt-4">
              <li>Free tier: 7 days trace retention</li>
              <li>Starter: 14 days trace retention</li>
              <li>Pro: 30 days trace retention</li>
              <li>Team: 60 days trace retention</li>
              <li>Enterprise: Up to 1 year (customizable)</li>
            </ul>
            <p className="text-gray-300 mt-4">
              Upon account deletion, we retain data for 30 days (recovery period), then permanently delete it within 90 days.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">8. International Data Transfers</h2>
            <p className="text-gray-300 leading-relaxed">
              Your data may be transferred to and processed in countries outside your residence. We ensure appropriate safeguards through Standard Contractual Clauses (SCCs) and other legally recognized transfer mechanisms.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">9. Children&apos;s Privacy</h2>
            <p className="text-gray-300 leading-relaxed">
              OverseeX is not intended for users under 16. We do not knowingly collect personal information from children. If we discover such data, we will delete it promptly.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">10. Changes to This Policy</h2>
            <p className="text-gray-300 leading-relaxed">
              We may update this Privacy Policy periodically. We will notify you of significant changes via email or platform notification. Continued use after changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">11. Contact Us</h2>
            <p className="text-gray-300 leading-relaxed">
              For privacy-related inquiries or to exercise your rights:
            </p>
            <div className="mt-4 p-6 rounded-xl bg-white/5 border border-white/10">
              <p className="text-gray-300">
                <strong className="text-white">Data Protection Officer</strong><br />
                OverseeX, Inc.<br />
                Email: <a href="mailto:privacy@overseex.com" className="text-violet-400 hover:underline">privacy@overseex.com</a><br />
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
            <Link href="/privacy" className="text-violet-400">Privacy</Link>
            <Link href="/cookies" className="text-gray-400 hover:text-white transition-colors">Cookies</Link>
            <Link href="/refund" className="text-gray-400 hover:text-white transition-colors">Refund Policy</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

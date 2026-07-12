"use client"

import Link from 'next/link'
import { Shield, ArrowLeft, Cookie, Settings } from 'lucide-react'

export default function CookiePolicyPage() {
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
        <h1 className="text-4xl font-medium mb-4">Cookie Policy</h1>
        <p className="text-gray-400 mb-12">Last updated: January 24, 2026</p>

        <div className="prose prose-invert prose-violet max-w-none">
          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">1. What Are Cookies?</h2>
            <p className="text-gray-300 leading-relaxed">
              Cookies are small text files stored on your device when you visit a website. They help websites remember your preferences, understand how you use the site, and provide personalized experiences. Some cookies are essential for the website to function, while others are optional.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">2. Types of Cookies We Use</h2>

            {/* Necessary Cookies */}
            <div className="p-6 rounded-xl bg-white/5 border border-white/10 mb-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                  <Cookie className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h3 className="font-medium text-white">Necessary Cookies</h3>
                  <span className="text-xs text-emerald-400">Always Active</span>
                </div>
              </div>
              <p className="text-gray-300 text-sm mb-3">
                Essential for the website to function. Without these, you cannot use core features.
              </p>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-2 text-gray-400">Cookie</th>
                    <th className="text-left py-2 text-gray-400">Purpose</th>
                    <th className="text-left py-2 text-gray-400">Expiry</th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  <tr className="border-b border-white/5">
                    <td className="py-2 font-mono text-xs">ag_session</td>
                    <td className="py-2">User authentication session</td>
                    <td className="py-2">Session</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="py-2 font-mono text-xs">ag_csrf</td>
                    <td className="py-2">Cross-site request forgery protection</td>
                    <td className="py-2">Session</td>
                  </tr>
                  <tr>
                    <td className="py-2 font-mono text-xs">ag_cookie_consent</td>
                    <td className="py-2">Stores your cookie preferences</td>
                    <td className="py-2">1 year</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Analytics Cookies */}
            <div className="p-6 rounded-xl bg-white/5 border border-white/10 mb-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Cookie className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-medium text-white">Analytics Cookies</h3>
                  <span className="text-xs text-gray-400">Optional</span>
                </div>
              </div>
              <p className="text-gray-300 text-sm mb-3">
                Help us understand how visitors interact with our website to improve the user experience.
              </p>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-2 text-gray-400">Cookie</th>
                    <th className="text-left py-2 text-gray-400">Purpose</th>
                    <th className="text-left py-2 text-gray-400">Expiry</th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  <tr className="border-b border-white/5">
                    <td className="py-2 font-mono text-xs">_ga</td>
                    <td className="py-2">Google Analytics - distinguishes users</td>
                    <td className="py-2">2 years</td>
                  </tr>
                  <tr>
                    <td className="py-2 font-mono text-xs">_gid</td>
                    <td className="py-2">Google Analytics - distinguishes users</td>
                    <td className="py-2">24 hours</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Marketing Cookies */}
            <div className="p-6 rounded-xl bg-white/5 border border-white/10 mb-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Cookie className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="font-medium text-white">Marketing Cookies</h3>
                  <span className="text-xs text-gray-400">Optional</span>
                </div>
              </div>
              <p className="text-gray-300 text-sm mb-3">
                Used to track visitors across websites for advertising purposes and to show relevant ads.
              </p>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-2 text-gray-400">Cookie</th>
                    <th className="text-left py-2 text-gray-400">Purpose</th>
                    <th className="text-left py-2 text-gray-400">Expiry</th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  <tr className="border-b border-white/5">
                    <td className="py-2 font-mono text-xs">_fbp</td>
                    <td className="py-2">Facebook Pixel tracking</td>
                    <td className="py-2">3 months</td>
                  </tr>
                  <tr>
                    <td className="py-2 font-mono text-xs">li_sugr</td>
                    <td className="py-2">LinkedIn Insight Tag</td>
                    <td className="py-2">3 months</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Preference Cookies */}
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                  <Settings className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h3 className="font-medium text-white">Preference Cookies</h3>
                  <span className="text-xs text-gray-400">Optional</span>
                </div>
              </div>
              <p className="text-gray-300 text-sm mb-3">
                Remember your settings and preferences for a better experience.
              </p>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-2 text-gray-400">Cookie</th>
                    <th className="text-left py-2 text-gray-400">Purpose</th>
                    <th className="text-left py-2 text-gray-400">Expiry</th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  <tr className="border-b border-white/5">
                    <td className="py-2 font-mono text-xs">ag_theme</td>
                    <td className="py-2">Theme preference (dark/light)</td>
                    <td className="py-2">1 year</td>
                  </tr>
                  <tr>
                    <td className="py-2 font-mono text-xs">ag_locale</td>
                    <td className="py-2">Language preference</td>
                    <td className="py-2">1 year</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">3. Managing Cookies</h2>
            <p className="text-gray-300 leading-relaxed mb-4">
              You can manage your cookie preferences in several ways:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2">
              <li><strong>Our Cookie Banner:</strong> Use the cookie consent banner to customize which cookies you accept</li>
              <li><strong>Browser Settings:</strong> Most browsers allow you to control cookies through their settings</li>
              <li><strong>Account Settings:</strong> Logged-in users can manage preferences in Settings → Privacy</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">4. Browser-Specific Instructions</h2>
            <div className="grid gap-3">
              {[
                { browser: 'Chrome', url: 'https://support.google.com/chrome/answer/95647' },
                { browser: 'Firefox', url: 'https://support.mozilla.org/en-US/kb/clear-cookies-and-site-data-firefox' },
                { browser: 'Safari', url: 'https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac' },
                { browser: 'Edge', url: 'https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09' },
              ].map((item) => (
                <a
                  key={item.browser}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 hover:border-violet-500/50 transition-colors group"
                >
                  <span className="text-gray-300">{item.browser}</span>
                  <span className="text-violet-400 group-hover:underline text-sm">View instructions →</span>
                </a>
              ))}
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">5. Third-Party Cookies</h2>
            <p className="text-gray-300 leading-relaxed">
              Some cookies are set by third-party services that appear on our pages. We do not control these cookies. Please refer to the respective third-party privacy policies for more information:
            </p>
            <ul className="list-disc list-inside text-gray-300 space-y-2 mt-4">
              <li><a href="https://policies.google.com/privacy" className="text-violet-400 hover:underline">Google Analytics Privacy Policy</a></li>
              <li><a href="https://www.facebook.com/policy.php" className="text-violet-400 hover:underline">Facebook Privacy Policy</a></li>
              <li><a href="https://www.linkedin.com/legal/privacy-policy" className="text-violet-400 hover:underline">LinkedIn Privacy Policy</a></li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">6. Updates to This Policy</h2>
            <p className="text-gray-300 leading-relaxed">
              We may update this Cookie Policy from time to time. Changes will be posted on this page with an updated revision date. For significant changes, we may notify you via email or a notice on our website.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-medium text-white mb-4">7. Contact Us</h2>
            <p className="text-gray-300 leading-relaxed">
              If you have questions about our use of cookies:
            </p>
            <div className="mt-4 p-6 rounded-xl bg-white/5 border border-white/10">
              <p className="text-gray-300">
                <strong className="text-white">Privacy Team</strong><br />
                Email: <a href="mailto:privacy@overseex.com" className="text-violet-400 hover:underline">privacy@overseex.com</a>
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
            <Link href="/cookies" className="text-violet-400">Cookies</Link>
            <Link href="/refund" className="text-gray-400 hover:text-white transition-colors">Refund Policy</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Cookie, X, Settings, Check } from 'lucide-react'
import Link from 'next/link'

interface CookiePreferences {
  necessary: boolean
  analytics: boolean
  marketing: boolean
  preferences: boolean
}

const COOKIE_CONSENT_KEY = 'overseex_cookie_consent'
const COOKIE_PREFERENCES_KEY = 'overseex_cookie_preferences'

export function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true, // Always required
    analytics: false,
    marketing: false,
    preferences: false,
  })

  useEffect(() => {
    // Check if user has already consented
    const consent = localStorage.getItem(COOKIE_CONSENT_KEY)
    if (!consent) {
      // Small delay before showing banner
      const timer = setTimeout(() => setIsVisible(true), 1500)
      return () => clearTimeout(timer)
    } else {
      // Load saved preferences
      const savedPrefs = localStorage.getItem(COOKIE_PREFERENCES_KEY)
      if (savedPrefs) {
        setPreferences(JSON.parse(savedPrefs))
      }
    }
  }, [])

  const acceptAll = () => {
    const allAccepted: CookiePreferences = {
      necessary: true,
      analytics: true,
      marketing: true,
      preferences: true,
    }
    saveConsent(allAccepted)
  }

  const acceptSelected = () => {
    saveConsent(preferences)
  }

  const rejectAll = () => {
    const onlyNecessary: CookiePreferences = {
      necessary: true,
      analytics: false,
      marketing: false,
      preferences: false,
    }
    saveConsent(onlyNecessary)
  }

  const saveConsent = (prefs: CookiePreferences) => {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'true')
    localStorage.setItem(COOKIE_PREFERENCES_KEY, JSON.stringify(prefs))
    setPreferences(prefs)
    setIsVisible(false)

    // Dispatch custom event for GoogleAnalytics component to react
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('cookieConsentUpdate', { detail: prefs }))
    }
  }

  const togglePreference = (key: keyof CookiePreferences) => {
    if (key === 'necessary') return // Can't toggle necessary cookies
    setPreferences(prev => ({ ...prev, [key]: !prev[key] }))
  }

  if (!isVisible) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        className="fixed bottom-0 left-0 right-0 z-50 p-4 md:p-6"
      >
        <div className="max-w-4xl mx-auto">
          <div 
            className="rounded-[26px] border overflow-hidden bg-black"
            style={{
              borderColor: 'rgba(255, 255, 255, 0.15)'
            }}
          >
            {!showSettings ? (
              // Simple consent view
              <div className="p-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(180deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)' }}>
                    <Cookie className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-white mb-2">We value your privacy</h3>
                    <p className="text-sm text-white/80 mb-4">
                      We use cookies to enhance your experience, analyze site traffic, and for marketing purposes. 
                      By clicking &quot;Accept All&quot;, you consent to our use of cookies. 
                      Read our{' '}
                      <Link href="/privacy" className="text-white underline hover:text-white/80">Privacy Policy</Link>
                      {' '}and{' '}
                      <Link href="/cookies" className="text-white underline hover:text-white/80">Cookie Policy</Link>
                      {' '}to learn more.
                    </p>
                    <div className="flex flex-wrap items-center gap-3">
                      <button
                        onClick={acceptAll}
                        className="px-5 py-2.5 text-black text-sm font-medium rounded-[10px] transition-all"
                        style={{ backgroundColor: 'rgb(239, 238, 236)' }}
                      >
                        Accept All
                      </button>
                      <button
                        onClick={rejectAll}
                        className="px-5 py-2.5 text-white text-sm font-medium rounded-[10px] transition-all"
                        style={{ backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
                      >
                        Reject All
                      </button>
                      <button
                        onClick={() => setShowSettings(true)}
                        className="px-5 py-2.5 text-white text-sm font-medium hover:text-white/80 transition-colors flex items-center gap-2"
                      >
                        <Settings className="w-4 h-4" />
                        Customize
                      </button>
                    </div>
                  </div>
                  <button
                    onClick={rejectAll}
                    className="text-white/60 hover:text-white transition-colors p-1"
                    aria-label="Close"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ) : (
              // Detailed settings view
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-medium text-white">Cookie Preferences</h3>
                  <button
                    onClick={() => setShowSettings(false)}
                    className="text-gray-500 hover:text-white transition-colors p-1"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                <div className="space-y-4 mb-6">
                  {/* Necessary Cookies */}
                  <div className="flex items-center justify-between p-4 rounded-xl border" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', borderColor: 'rgba(255, 255, 255, 0.15)' }}>
                    <div>
                      <h4 className="font-medium text-white mb-1">Necessary Cookies</h4>
                      <p className="text-sm text-white/80">
                        Required for the website to function properly. Cannot be disabled.
                      </p>
                    </div>
                    <div className="w-12 h-6 rounded-full flex items-center justify-end px-1" style={{ backgroundColor: 'rgb(239, 238, 236)' }}>
                      <div className="w-4 h-4 bg-black rounded-full" />
                    </div>
                  </div>

                  {/* Analytics Cookies */}
                  <div className="flex items-center justify-between p-4 rounded-xl border" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', borderColor: 'rgba(255, 255, 255, 0.15)' }}>
                    <div>
                      <h4 className="font-medium text-white mb-1">Analytics Cookies</h4>
                      <p className="text-sm text-white/80">
                        Help us understand how visitors interact with our website.
                      </p>
                    </div>
                    <button
                      onClick={() => togglePreference('analytics')}
                      className="w-12 h-6 rounded-full flex items-center px-1 transition-colors"
                      style={{
                        backgroundColor: preferences.analytics ? 'rgb(239, 238, 236)' : 'rgba(255, 255, 255, 0.2)',
                        justifyContent: preferences.analytics ? 'flex-end' : 'flex-start'
                      }}
                    >
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: preferences.analytics ? '#000' : '#fff' }} />
                    </button>
                  </div>

                  {/* Marketing Cookies */}
                  <div className="flex items-center justify-between p-4 rounded-xl border" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', borderColor: 'rgba(255, 255, 255, 0.15)' }}>
                    <div>
                      <h4 className="font-medium text-white mb-1">Marketing Cookies</h4>
                      <p className="text-sm text-white/80">
                        Used to track visitors across websites for advertising purposes.
                      </p>
                    </div>
                    <button
                      onClick={() => togglePreference('marketing')}
                      className="w-12 h-6 rounded-full flex items-center px-1 transition-colors"
                      style={{
                        backgroundColor: preferences.marketing ? 'rgb(239, 238, 236)' : 'rgba(255, 255, 255, 0.2)',
                        justifyContent: preferences.marketing ? 'flex-end' : 'flex-start'
                      }}
                    >
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: preferences.marketing ? '#000' : '#fff' }} />
                    </button>
                  </div>

                  {/* Preference Cookies */}
                  <div className="flex items-center justify-between p-4 rounded-xl border" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', borderColor: 'rgba(255, 255, 255, 0.15)' }}>
                    <div>
                      <h4 className="font-medium text-white mb-1">Preference Cookies</h4>
                      <p className="text-sm text-white/80">
                        Allow us to remember your preferences and settings.
                      </p>
                    </div>
                    <button
                      onClick={() => togglePreference('preferences')}
                      className="w-12 h-6 rounded-full flex items-center px-1 transition-colors"
                      style={{
                        backgroundColor: preferences.preferences ? 'rgb(239, 238, 236)' : 'rgba(255, 255, 255, 0.2)',
                        justifyContent: preferences.preferences ? 'flex-end' : 'flex-start'
                      }}
                    >
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: preferences.preferences ? '#000' : '#fff' }} />
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3">
                  <button
                    onClick={rejectAll}
                    className="px-5 py-2.5 text-white text-sm font-medium hover:text-white/80 transition-colors"
                  >
                    Reject All
                  </button>
                  <button
                    onClick={acceptSelected}
                    className="px-5 py-2.5 text-black text-sm font-medium rounded-[10px] transition-all flex items-center gap-2"
                    style={{ backgroundColor: 'rgb(239, 238, 236)' }}
                  >
                    <Check className="w-4 h-4" />
                    Save Preferences
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

// Export a hook to check cookie preferences
export function useCookiePreferences() {
  const [preferences, setPreferences] = useState<CookiePreferences | null>(null)

  useEffect(() => {
    const savedPrefs = localStorage.getItem(COOKIE_PREFERENCES_KEY)
    if (savedPrefs) {
      setPreferences(JSON.parse(savedPrefs))
    }
  }, [])

  return preferences
}

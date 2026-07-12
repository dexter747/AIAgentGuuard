'use client'

import { useEffect, useState } from 'react'
import Script from 'next/script'

const GA_MEASUREMENT_ID = 'G-KRP5J1N86H'
const COOKIE_PREFERENCES_KEY = 'overseex_cookie_preferences'

interface CookiePreferences {
  necessary: boolean
  analytics: boolean
  marketing: boolean
  preferences: boolean
}

export function GoogleAnalytics() {
  const [analyticsEnabled, setAnalyticsEnabled] = useState(true) // Default to true for proper GA tag detection

  useEffect(() => {
    // Check if user has explicitly disabled analytics
    const checkPreferences = () => {
      const savedPrefs = localStorage.getItem(COOKIE_PREFERENCES_KEY)
      if (savedPrefs) {
        const prefs: CookiePreferences = JSON.parse(savedPrefs)
        setAnalyticsEnabled(prefs.analytics)
      }
      // If no preference saved, keep enabled by default
    }

    checkPreferences()

    // Listen for storage changes (when user updates preferences)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === COOKIE_PREFERENCES_KEY) {
        checkPreferences()
      }
    }

    // Also listen for custom events from CookieConsent
    const handleConsentUpdate = () => {
      checkPreferences()
    }

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('cookieConsentUpdate', handleConsentUpdate)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('cookieConsentUpdate', handleConsentUpdate)
    }
  }, [])

  // Don't render anything if analytics not consented
  if (!analyticsEnabled) {
    return null
  }

  return (
    <>
      {/* Google Analytics Script */}
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_MEASUREMENT_ID}', {
            page_path: window.location.pathname,
            anonymize_ip: true,
            cookie_flags: 'SameSite=None;Secure'
          });
        `}
      </Script>
    </>
  )
}

// Export pageview function for route changes
export const pageview = (url: string) => {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('config', GA_MEASUREMENT_ID, {
      page_path: url,
    })
  }
}

// Export event tracking function
export const trackEvent = ({
  action,
  category,
  label,
  value,
}: {
  action: string
  category: string
  label?: string
  value?: number
}) => {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    })
  }
}

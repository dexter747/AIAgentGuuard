'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function DocsRedirect() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to external docs portal
    window.location.href = 'https://docs.overseex.com'
  }, [])

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Redirecting to documentation...</p>
        <a
          href="https://docs.overseex.com"
          className="text-violet-400 hover:text-violet-300 mt-4 inline-block"
        >
          Click here if not redirected
        </a>
      </div>
    </div>
  )
}

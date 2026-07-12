'use client'

import { useState, useEffect, useRef, Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Shield, CheckCircle, XCircle, Loader2, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'

export const dynamic = 'force-dynamic'

function VerifyEmailContent() {
  const searchParams = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState('')
  const hasVerified = useRef(false) // Prevent double execution in StrictMode

  useEffect(() => {
    const verifyEmail = async () => {
      // Prevent duplicate calls
      if (hasVerified.current) return
      hasVerified.current = true

      if (!token) {
        setStatus('error')
        setMessage('Invalid verification link')
        return
      }

      try {
        const response = await fetch(`${API_URL}/api/v1/auth/verify-email`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        })

        const data = await response.json()

        if (response.ok) {
          setStatus('success')
          setMessage(data.message || 'Email verified successfully!')
        } else {
          setStatus('error')
          setMessage(data.detail || 'Verification failed')
        }
      } catch (err) {
        setStatus('error')
        setMessage('Failed to connect to server. Please try again.')
      }
    }

    verifyEmail()
  }, [token])

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-violet-600/20 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-purple-600/15 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-3 mb-8">
          <img 
            src="/logo.jpeg" 
            alt="OverseeX" 
            className="h-12 w-auto"
          />
          <span className="text-2xl font-medium text-white">OverseeX</span>
        </Link>

        <Card className="bg-gradient-to-br from-gray-950 to-black border-white/10 backdrop-blur-xl">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-white text-center">
              {status === 'verifying' && 'Verifying Email...'}
              {status === 'success' && 'Email Verified!'}
              {status === 'error' && 'Verification Failed'}
            </CardTitle>
            <CardDescription className="text-center text-gray-400">
              {status === 'verifying' && 'Please wait while we verify your email address'}
              {status === 'success' && 'Your account is now active'}
              {status === 'error' && 'Something went wrong'}
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center py-6">
            {status === 'verifying' && (
              <div className="w-16 h-16 rounded-full bg-violet-500/20 flex items-center justify-center mx-auto mb-4">
                <Loader2 className="h-8 w-8 text-violet-400 animate-spin" />
              </div>
            )}

            {status === 'success' && (
              <>
                <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="h-8 w-8 text-emerald-400" />
                </div>
                <p className="text-sm text-gray-400 mb-6">
                  {message}
                </p>
                <Link href="/signin">
                  <Button className="w-full bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white font-medium shadow-lg shadow-violet-500/25">
                    Sign In to Your Account
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
                  <XCircle className="h-8 w-8 text-red-400" />
                </div>
                <p className="text-sm text-red-400 mb-6">
                  {message}
                </p>
                <div className="space-y-3">
                  <Link href="/signin">
                    <Button variant="outline" className="bg-white/5 border-white/10 text-white hover:bg-white/10 w-full">
                      Go to Sign In
                    </Button>
                  </Link>
                  <p className="text-xs text-gray-500">
                    If you continue to have issues, please contact{' '}
                    <a href="mailto:support@overseex.com" className="text-violet-400 hover:text-violet-300">
                      support@overseex.com
                    </a>
                  </p>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-violet-950 to-slate-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-violet-400" />
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  )
}

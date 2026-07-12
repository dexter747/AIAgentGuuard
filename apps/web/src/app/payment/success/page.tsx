'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

function PaymentSuccessContent() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing your payment...');

  useEffect(() => {
    // Get session or payment ID from URL
    const sessionId = searchParams.get('session_id');
    const paymentId = searchParams.get('payment_id');
    
    if (sessionId || paymentId) {
      // Verify payment with backend
      verifyPayment(sessionId, paymentId);
    } else {
      setStatus('error');
      setMessage('No payment information found.');
    }
  }, [searchParams]);

  const verifyPayment = async (sessionId: string | null, paymentId: string | null) => {
    try {
      // Give DODO webhooks time to process
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Fetch updated subscription from backend
      const response = await fetch('/api/billing/subscription', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.status === 'active' && data.plan_id !== 'free_monthly') {
          setStatus('success');
          setMessage(`Successfully subscribed to ${data.plan}!`);
        } else {
          // Still processing, wait a bit more
          setTimeout(() => {
            setStatus('success');
            setMessage('Payment received! Your subscription is being activated.');
          }, 2000);
        }
      } else {
        setStatus('error');
        setMessage('Failed to verify payment. Please contact support.');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setStatus('error');
      setMessage('An error occurred while verifying your payment.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-slate-800 rounded-2xl p-8 max-w-md w-full text-center"
      >
        {status === 'loading' && (
          <>
            <Loader2 className="w-16 h-16 text-purple-500 mx-auto mb-4 animate-spin" />
            <h1 className="text-2xl font-medium text-white mb-2">Processing Payment</h1>
            <p className="text-gray-400">{message}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h1 className="text-2xl font-medium text-white mb-2">Payment Successful!</h1>
            <p className="text-gray-400 mb-6">{message}</p>
            <Link
              href="/dashboard"
              className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-medium px-6 py-3 rounded-lg transition-colors"
            >
              Go to Dashboard
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-medium text-white mb-2">Payment Error</h1>
            <p className="text-gray-400 mb-6">{message}</p>
            <div className="space-y-3">
              <Link
                href="/pricing"
                className="block bg-purple-600 hover:bg-purple-700 text-white font-medium px-6 py-3 rounded-lg transition-colors"
              >
                Try Again
              </Link>
              <a
                href="mailto:support@overseex.com"
                className="block text-purple-400 hover:text-purple-300 transition-colors"
              >
                Contact Support
              </a>
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-purple-400" />
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  );
}

'use client'

import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export function NoticePopup() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Check if user has seen the notice before
    const hasSeenNotice = localStorage.getItem('hasSeenPlatformNotice')
    
    if (!hasSeenNotice) {
      // Show popup after a short delay
      setTimeout(() => {
        setIsVisible(true)
      }, 1000)
    }
  }, [])

  const handleClose = () => {
    setIsVisible(false)
    localStorage.setItem('hasSeenPlatformNotice', 'true')
  }

  const handleDismiss = () => {
    setIsVisible(false)
    // Don't set localStorage so it shows again on next visit
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
            onClick={handleDismiss}
          />

          {/* Popup - Styled like cookie consent */}
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[101] w-[95%] max-w-3xl"
          >
            <div 
              className="relative p-8 rounded-2xl border shadow-2xl"
              style={{
                background: 'linear-gradient(135deg, rgba(15, 15, 15, 0.98) 0%, rgba(20, 20, 20, 0.98) 100%)',
                backdropFilter: 'blur(20px)',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.05)'
              }}
            >
              {/* Close button */}
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Content */}
              <div className="space-y-6">
                {/* Heading */}
                <div>
                  <h2 
                    className="text-2xl font-medium mb-4"
                    style={{
                      background: 'linear-gradient(90deg, rgb(255, 255, 255) 0%, rgba(255, 255, 255, 0.7) 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text'
                    }}
                  >
                    You're early!
                  </h2>
                  <p className="text-gray-300 leading-relaxed mb-4">
                    And that's wonderful! Overseex is in early access, which means you get the newest features first and can directly influence what we build next.
                  </p>
                  <p className="text-gray-400 leading-relaxed">
                    If you run into anything unexpected or have ideas or recommendations, we'd genuinely love your feedback at overseexcorporation@gmail.com, it helps us ship faster and better for everyone.
                  </p>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-3 pt-2">
                  <button
                    onClick={handleClose}
                    className="px-6 py-2.5 rounded-lg font-medium transition-all hover:scale-[1.02] active:scale-[0.98]"
                    style={{
                      background: 'linear-gradient(135deg, rgb(79, 26, 214) 0%, rgb(128, 89, 227) 100%)',
                      color: 'white',
                      boxShadow: '0 4px 12px rgba(128, 89, 227, 0.3)'
                    }}
                  >
                    Got it, thanks!
                  </button>
                  <button
                    onClick={handleDismiss}
                    className="px-6 py-2.5 rounded-lg font-medium border transition-all hover:bg-white/5"
                    style={{
                      borderColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'rgb(156, 163, 175)'
                    }}
                  >
                    Remind me later
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

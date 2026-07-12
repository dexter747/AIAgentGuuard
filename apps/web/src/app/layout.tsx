import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { CookieConsent } from '@/components/CookieConsent'
import { GoogleAnalytics } from '@/components/GoogleAnalytics'

const inter = Inter({ subsets: ['latin'] })

// Comprehensive SEO keywords for AI agent monitoring
const keywords = [
  // Core product keywords
  'AI agent monitoring', 'AI agent testing', 'LLM monitoring', 'LLM observability',
  'multi-agent coordination', 'AI agent tracing', 'AI debugging', 'AI observability platform',

  // Framework integrations
  'LangChain monitoring', 'LangChain tracing', 'LangGraph monitoring', 'CrewAI monitoring',
  'AutoGen monitoring', 'AutoGen tracing', 'OpenAI monitoring', 'GPT monitoring',
  'Claude monitoring', 'Anthropic API monitoring', 'Vercel AI SDK monitoring',

  // Technical terms
  'LLM tracing', 'AI agent analytics', 'AI agent performance', 'AI agent debugging',
  'multi-agent systems', 'agent coordination', 'agent handoff tracking', 'state drift detection',
  'AI regression testing', 'AI quality assurance', 'AI agent reliability',

  // Use cases
  'AI production monitoring', 'AI cost tracking', 'LLM cost optimization', 'AI error tracking',
  'AI agent logs', 'AI trace visualization', 'AI span tracking', 'distributed AI tracing',

  // Industry terms
  'MLOps', 'LLMOps', 'AI infrastructure', 'AI platform', 'AI development tools',
  'AI engineering', 'AI DevOps', 'machine learning monitoring', 'ML observability',

  // Competitive keywords
  'LangSmith alternative', 'Weights and Biases alternative', 'Datadog AI monitoring',
  'AI monitoring solution', 'enterprise AI monitoring', 'AI agent platform',

  // Action keywords
  'monitor AI agents', 'debug AI agents', 'test AI agents', 'trace LLM calls',
  'optimize AI costs', 'track AI performance', 'analyze AI behavior',

  // Feature keywords
  'real-time AI monitoring', 'AI alerting', 'AI dashboards', 'AI metrics',
  'AI agent SDK', 'Python AI monitoring', 'JavaScript AI monitoring', 'TypeScript AI SDK',
  'PII redaction AI', 'AI security monitoring', 'AI compliance', 'AI audit logs',

  // Integration keywords
  'n8n AI monitoring', 'Make automation AI', 'Zapier AI integration', 'workflow AI monitoring',
  'API monitoring AI', 'webhook AI integration', 'REST API AI tracing',

  // Business keywords
  'AI agent startup', 'AI SaaS', 'AI monitoring service', 'AI observability tool',
  'AI debugging tool', 'AI testing tool', 'AI quality tool', 'AI reliability tool',

  // Long-tail keywords
  'how to monitor AI agents', 'best AI monitoring tools', 'AI agent testing best practices',
  'multi-agent coordination patterns', 'LLM application debugging', 'AI agent performance optimization',
  'reduce AI costs', 'AI agent error handling', 'AI agent failure detection',

  // Technology stack
  'FastAPI AI', 'Next.js AI dashboard', 'PostgreSQL AI', 'Redis AI caching',
  'Docker AI deployment', 'Kubernetes AI', 'cloud AI monitoring',

  // Emerging trends
  'agentic AI monitoring', 'autonomous AI agents', 'AI agent orchestration',
  'conversational AI monitoring', 'chatbot monitoring', 'AI assistant monitoring',
  'RAG monitoring', 'retrieval augmented generation', 'vector database monitoring',

  // Security and compliance
  'AI data privacy', 'GDPR AI compliance', 'SOC2 AI', 'AI audit trail',
  'AI governance', 'responsible AI monitoring', 'AI ethics monitoring',

  // Performance keywords
  'AI latency monitoring', 'AI throughput tracking', 'AI token usage', 'AI rate limiting',
  'AI quota management', 'AI usage analytics', 'AI billing monitoring',
].join(', ')

export const metadata: Metadata = {
  metadataBase: new URL('https://overseex.com'),
  title: {
    default: 'OverseeX - AI Agent Testing & Monitoring Platform',
    template: '%s | OverseeX',
  },
  description: 'The complete testing and monitoring platform for AI agents. Debug, trace, and optimize your LLM applications with real-time observability, multi-agent coordination intelligence, and automated regression detection.',
  keywords: keywords,
  authors: [{ name: 'OverseeX Team', url: 'https://overseex.com' }],
  creator: 'OverseeX',
  publisher: 'OverseeX',
  applicationName: 'OverseeX',
  category: 'Technology',
  classification: 'AI Monitoring Software',

  // Open Graph
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://overseex.com',
    siteName: 'OverseeX',
    title: 'OverseeX - AI Agent Testing & Monitoring Platform',
    description: 'The complete testing and monitoring platform for AI agents. Debug, trace, and optimize your LLM applications with real-time observability.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'OverseeX - AI Agent Monitoring',
      },
    ],
  },

  // Twitter Card
  twitter: {
    card: 'summary_large_image',
    title: 'OverseeX - AI Agent Testing & Monitoring',
    description: 'The complete testing and monitoring platform for AI agents. Real-time observability for LLM applications.',
    images: ['/og-image.png'],
    creator: '@overseex',
    site: '@overseex',
  },

  // Robots
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },

  // Verification
  verification: {
    google: 'google-site-verification-code',
  },

  // Alternate languages
  alternates: {
    canonical: 'https://overseex.com',
    languages: {
      'en-US': 'https://overseex.com',
    },
  },

  // Icons
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },

  // Manifest
  manifest: '/manifest.json',

  // Additional metadata
  other: {
    'msapplication-TileColor': '#7c3aed',
    'theme-color': '#000000',
  },
}

// JSON-LD structured data
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'OverseeX',
  applicationCategory: 'DeveloperApplication',
  operatingSystem: 'Web',
  description: 'The complete testing and monitoring platform for AI agents. Debug, trace, and optimize your LLM applications.',
  url: 'https://overseex.com',
  author: {
    '@type': 'Organization',
    name: 'OverseeX',
    url: 'https://overseex.com',
  },
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
    description: 'Free tier available',
  },
  featureList: [
    'AI Agent Monitoring',
    'LLM Tracing',
    'Multi-Agent Coordination',
    'Real-time Observability',
    'Regression Detection',
    'Cost Tracking',
    'PII Redaction',
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className={inter.className}>
        <GoogleAnalytics />
        {children}
        <CookieConsent />
      </body>
    </html>
  )
}

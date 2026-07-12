import { MetadataRoute } from 'next'

const BASE_URL = 'https://overseex.com'

// Blog post slugs - add new posts here
const blogSlugs = [
  'introduction-to-ai-agent-monitoring',
  'multi-agent-coordination-best-practices',
  'debugging-llm-applications',
  'langchain-integration-guide',
  'crewai-monitoring-tutorial',
  'autogen-tracing-setup',
  'ai-agent-security-best-practices',
  'cost-optimization-llm-apps',
  'real-time-ai-observability',
  'future-of-multi-agent-systems',
]

export default function sitemap(): MetadataRoute.Sitemap {
  const currentDate = new Date().toISOString()

  // Main pages
  const mainPages: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: currentDate,
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${BASE_URL}/features`,
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/pricing`,
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/blog`,
      lastModified: currentDate,
      changeFrequency: 'daily',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/login`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${BASE_URL}/register`,
      lastModified: currentDate,
      changeFrequency: 'monthly',
      priority: 0.5,
    },
  ]

  // Blog posts
  const blogPages: MetadataRoute.Sitemap = blogSlugs.map((slug) => ({
    url: `${BASE_URL}/blog/${slug}`,
    lastModified: currentDate,
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }))

  // Documentation pages
  const docPages: MetadataRoute.Sitemap = [
    {
      url: 'https://docs.overseex.com',
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: 'https://docs.overseex.com/python',
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: 'https://docs.overseex.com/javascript',
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: 'https://docs.overseex.com/langchain',
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: 'https://docs.overseex.com/crewai',
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: 'https://docs.overseex.com/autogen',
      lastModified: currentDate,
      changeFrequency: 'weekly',
      priority: 0.8,
    },
  ]

  // Feature pages
  const featurePages: MetadataRoute.Sitemap = [
    'agent-monitoring',
    'trace-visualization',
    'multi-agent-coordination',
    'regression-detection',
    'pii-redaction',
    'real-time-alerts',
    'cost-tracking',
    'performance-analytics',
  ].map((feature) => ({
    url: `${BASE_URL}/features/${feature}`,
    lastModified: currentDate,
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }))

  return [...mainPages, ...blogPages, ...docPages, ...featurePages]
}

import { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { Navbar } from '@/components/Navbar'
import { getPostBySlug, getAllPosts } from '@/lib/blog-data'
import { Calendar, Clock, ArrowLeft, Share2, Twitter, Linkedin, Link as LinkIcon } from 'lucide-react'

interface Props {
  params: { slug: string }
}

export async function generateStaticParams() {
  const posts = getAllPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = getPostBySlug(params.slug)
  if (!post) return { title: 'Post Not Found' }

  return {
    title: post.title,
    description: post.excerpt,
    keywords: post.tags.join(', '),
    authors: [{ name: post.author }],
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.date,
      authors: [post.author],
      tags: post.tags,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
    },
  }
}

export default function BlogPostPage({ params }: Props) {
  const post = getPostBySlug(params.slug)

  if (!post) {
    notFound()
  }

  const allPosts = getAllPosts()
  const currentIndex = allPosts.findIndex(p => p.slug === post.slug)
  const relatedPosts = allPosts
    .filter(p => p.slug !== post.slug && p.category === post.category)
    .slice(0, 3)

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <main className="pt-24 pb-20">
        {/* Header */}
        <article className="px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
          {/* Back Link */}
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Blog
          </Link>

          {/* Category & Tags */}
          <div className="flex flex-wrap items-center gap-2 mb-6">
            <span className="px-3 py-1 text-sm font-medium bg-purple-500/20 text-purple-300 rounded-full">
              {post.category}
            </span>
            {post.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-3 py-1 text-sm bg-white/10 text-gray-300 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>

          {/* Title */}
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-medium mb-6 leading-tight">
            {post.title}
          </h1>

          {/* Meta */}
          <div className="flex flex-wrap items-center gap-6 mb-8 pb-8 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-lg font-medium">
                {post.author.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <p className="font-medium">{post.author}</p>
                <p className="text-sm text-gray-400">{post.authorRole}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-gray-400">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {new Date(post.date).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {post.readTime}
              </span>
            </div>
          </div>

          {/* Content */}
          <div
            className="prose prose-invert prose-lg max-w-none
              prose-headings:font-medium prose-headings:text-white
              prose-h1:text-3xl prose-h1:mt-12 prose-h1:mb-6
              prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4
              prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3
              prose-p:text-gray-300 prose-p:leading-relaxed
              prose-a:text-purple-400 prose-a:no-underline hover:prose-a:underline
              prose-strong:text-white
              prose-code:text-purple-300 prose-code:bg-white/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
              prose-pre:bg-white/5 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl
              prose-ul:text-gray-300 prose-ol:text-gray-300
              prose-li:marker:text-purple-400
              prose-blockquote:border-purple-500 prose-blockquote:text-gray-400"
            dangerouslySetInnerHTML={{ __html: formatContent(post.content) }}
          />

          {/* Share */}
          <div className="mt-12 pt-8 border-t border-white/10">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <Share2 className="w-5 h-5 text-gray-400" />
                <span className="text-gray-400">Share this article</span>
              </div>
              <div className="flex items-center gap-3">
                <button className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
                  <Twitter className="w-5 h-5" />
                </button>
                <button className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
                  <Linkedin className="w-5 h-5" />
                </button>
                <button className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
                  <LinkIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Author Bio */}
          <div className="mt-12 p-6 bg-white/5 border border-white/10 rounded-2xl">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xl font-medium flex-shrink-0">
                {post.author.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <p className="font-medium text-lg">{post.author}</p>
                <p className="text-purple-400 mb-2">{post.authorRole}</p>
                <p className="text-gray-400 text-sm">
                  Writing about AI agents, monitoring, and building reliable LLM applications at OverseeX.
                </p>
              </div>
            </div>
          </div>
        </article>

        {/* Related Posts */}
        {relatedPosts.length > 0 && (
          <div className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto mt-20">
            <h2 className="text-2xl font-medium mb-8">Related Articles</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {relatedPosts.map((relatedPost) => (
                <Link
                  key={relatedPost.slug}
                  href={`/blog/${relatedPost.slug}`}
                  className="group"
                >
                  <article className="h-full bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all">
                    <span className="px-3 py-1 text-xs font-medium bg-white/10 text-gray-300 rounded-full">
                      {relatedPost.category}
                    </span>
                    <h3 className="text-lg font-medium mt-4 mb-2 group-hover:text-purple-300 transition-colors line-clamp-2">
                      {relatedPost.title}
                    </h3>
                    <p className="text-gray-400 text-sm line-clamp-2">
                      {relatedPost.excerpt}
                    </p>
                  </article>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div className="px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto mt-20">
          <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-white/10 rounded-2xl p-8 text-center">
            <h2 className="text-2xl font-medium mb-3">Ready to Monitor Your AI Agents?</h2>
            <p className="text-gray-400 mb-6">
              Start capturing traces and optimizing your LLM applications today.
            </p>
            <Link
              href="/register"
              className="inline-block px-8 py-3 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}

function formatContent(content: string): string {
  // Convert markdown-style formatting to HTML
  let html = content
    // Headers
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Code blocks
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Lists
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    // Paragraphs
    .split('\n\n')
    .map(para => {
      if (para.startsWith('<h') || para.startsWith('<pre') || para.startsWith('<li')) {
        return para
      }
      if (para.includes('<li>')) {
        return `<ul>${para}</ul>`
      }
      if (para.trim()) {
        return `<p>${para}</p>`
      }
      return ''
    })
    .join('\n')

  return html
}

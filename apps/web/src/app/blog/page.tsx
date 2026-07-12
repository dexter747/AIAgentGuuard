"use client"

import Link from 'next/link'
import { Navbar } from '@/components/Navbar'
import { getAllPosts, getFeaturedPosts, getAllCategories } from '@/lib/blog-data'
import { Calendar, Clock, ArrowRight, Sparkles } from 'lucide-react'

export default function BlogPage() {
  const posts = getAllPosts()
  const featuredPosts = getFeaturedPosts()
  const categories = getAllCategories()

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <main className="pt-24 pb-20">
        {/* Hero Section */}
        <div className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto mb-16">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 mb-6">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-purple-300">Insights & Updates</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-medium mb-4">
              OverseeX Blog
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Expert insights on AI agent monitoring, multi-agent coordination, and building reliable LLM applications.
            </p>
          </div>
        </div>

        {/* Featured Posts */}
        {featuredPosts.length > 0 && (
          <div className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto mb-16">
            <h2 className="text-2xl font-medium mb-8">Featured Articles</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredPosts.map((post) => (
                <Link
                  key={post.slug}
                  href={`/blog/${post.slug}`}
                  className="group"
                >
                  <article className="h-full bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all duration-300">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="px-3 py-1 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-full">
                        Featured
                      </span>
                      <span className="px-3 py-1 text-xs font-medium bg-white/10 text-gray-300 rounded-full">
                        {post.category}
                      </span>
                    </div>
                    <h3 className="text-xl font-medium mb-3 group-hover:text-purple-300 transition-colors line-clamp-2">
                      {post.title}
                    </h3>
                    <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                      {post.excerpt}
                    </p>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {post.readTime}
                        </span>
                      </div>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Categories */}
        <div className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto mb-12">
          <div className="flex flex-wrap gap-3 justify-center">
            <button className="px-4 py-2 text-sm font-medium bg-white text-black rounded-full">
              All Posts
            </button>
            {categories.map((category) => (
              <button
                key={category}
                className="px-4 py-2 text-sm font-medium bg-white/10 text-white rounded-full hover:bg-white/20 transition-colors"
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* All Posts Grid */}
        <div className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map((post) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="group"
              >
                <article className="h-full bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:border-white/20 transition-all duration-300">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="px-3 py-1 text-xs font-medium bg-white/10 text-gray-300 rounded-full">
                      {post.category}
                    </span>
                  </div>
                  <h3 className="text-lg font-medium mb-3 group-hover:text-purple-300 transition-colors line-clamp-2">
                    {post.title}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                    {post.excerpt}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {post.readTime}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xs font-medium">
                      {post.author.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{post.author}</p>
                      <p className="text-xs text-gray-500">{post.authorRole}</p>
                    </div>
                  </div>
                </article>
              </Link>
            ))}
          </div>
        </div>

        {/* Newsletter CTA */}
        <div className="px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto mt-20">
          <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-white/10 rounded-2xl p-8 text-center">
            <h2 className="text-2xl font-medium mb-3">Stay Updated</h2>
            <p className="text-gray-400 mb-6">
              Get the latest insights on AI agent monitoring delivered to your inbox.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
              />
              <button className="px-6 py-3 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition-colors">
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

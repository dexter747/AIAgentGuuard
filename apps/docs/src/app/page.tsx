'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  Book,
  Code2,
  Zap,
  Activity,
  Key,
  Webhook,
  Terminal,
  Settings,
  ChevronRight,
  Search,
  ExternalLink,
  Menu,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Navbar } from '@/components/Navbar'
import { CodeBlock } from '@/components/CodeBlock'

// Platform tabs with icons
const platformTabs = [
  {
    id: 'python',
    name: 'Python',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z"/>
      </svg>
    )
  },
  {
    id: 'typescript',
    name: 'TypeScript',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M1.125 0C.502 0 0 .502 0 1.125v21.75C0 23.498.502 24 1.125 24h21.75c.623 0 1.125-.502 1.125-1.125V1.125C24 .502 23.498 0 22.875 0zm17.363 9.75c.612 0 1.154.037 1.627.111a6.38 6.38 0 0 1 1.306.34v2.458a3.95 3.95 0 0 0-.643-.361 5.093 5.093 0 0 0-.717-.26 5.453 5.453 0 0 0-1.426-.2c-.3 0-.573.028-.819.086a2.1 2.1 0 0 0-.623.242c-.17.104-.3.229-.393.374a.888.888 0 0 0-.14.49c0 .196.053.373.156.529.104.156.252.304.443.444s.423.276.696.41c.273.135.582.274.926.416.47.197.892.407 1.266.628.374.222.695.473.963.753.268.279.472.598.614.957.142.359.214.776.214 1.253 0 .657-.125 1.21-.373 1.656a3.033 3.033 0 0 1-1.012 1.085 4.38 4.38 0 0 1-1.487.596c-.566.12-1.163.18-1.79.18a9.916 9.916 0 0 1-1.84-.164 5.544 5.544 0 0 1-1.512-.493v-2.63a5.033 5.033 0 0 0 3.237 1.2c.333 0 .624-.03.872-.09.249-.06.456-.144.623-.25.166-.108.29-.234.373-.38a1.023 1.023 0 0 0-.074-1.089 2.12 2.12 0 0 0-.537-.5 5.597 5.597 0 0 0-.807-.444 27.72 27.72 0 0 0-1.007-.436c-.918-.383-1.602-.852-2.053-1.405-.45-.553-.676-1.222-.676-2.005 0-.614.123-1.141.369-1.582.246-.441.58-.804 1.004-1.089a4.494 4.494 0 0 1 1.47-.629 7.536 7.536 0 0 1 1.77-.201zm-15.113.188h9.563v2.166H9.506v9.646H6.789v-9.646H3.375z"/>
      </svg>
    )
  },
  {
    id: 'javascript',
    name: 'JavaScript',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M0 0h24v24H0V0zm22.034 18.276c-.175-1.095-.888-2.015-3.003-2.873-.736-.345-1.554-.585-1.797-1.14-.091-.33-.105-.51-.046-.705.15-.646.915-.84 1.515-.66.39.12.75.42.976.9 1.034-.676 1.034-.676 1.755-1.125-.27-.42-.404-.601-.586-.78-.63-.705-1.469-1.065-2.834-1.034l-.705.089c-.676.165-1.32.525-1.71 1.005-1.14 1.291-.811 3.541.569 4.471 1.365 1.02 3.361 1.244 3.616 2.205.24 1.17-.87 1.545-1.966 1.41-.811-.18-1.26-.586-1.755-1.336l-1.83 1.051c.21.48.45.689.81 1.109 1.74 1.756 6.09 1.666 6.871-1.004.029-.09.24-.705.074-1.65l.046.067zm-8.983-7.245h-2.248c0 1.938-.009 3.864-.009 5.805 0 1.232.063 2.363-.138 2.711-.33.689-1.18.601-1.566.48-.396-.196-.597-.466-.83-.855-.063-.105-.11-.196-.127-.196l-1.825 1.125c.305.63.75 1.172 1.324 1.517.855.51 2.004.675 3.207.405.783-.226 1.458-.691 1.811-1.411.51-.93.402-2.07.397-3.346.012-2.054 0-4.109 0-6.179l.004-.056z"/>
      </svg>
    )
  },
  {
    id: 'crewai',
    name: 'CrewAI',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
      </svg>
    )
  },
  {
    id: 'langchain',
    name: 'LangChain',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M13.5 2c-5.621 0-10.211 4.443-10.475 10h-3.025l5 6.625 5-6.625h-2.975c.257-3.351 3.06-6 6.475-6 3.584 0 6.5 2.916 6.5 6.5s-2.916 6.5-6.5 6.5c-1.863 0-3.542-.793-4.728-2.053l-2.427 3.216c1.877 1.754 4.389 2.837 7.155 2.837 5.79 0 10.5-4.71 10.5-10.5s-4.71-10.5-10.5-10.5z"/>
      </svg>
    )
  },
  {
    id: 'autogen',
    name: 'AutoGen',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
      </svg>
    )
  },
  {
    id: 'vercelai',
    name: 'Vercel AI',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M24 22.525H0l12-21.05 12 21.05z"/>
      </svg>
    )
  },
  {
    id: 'n8n',
    name: 'n8n',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 4.8a7.2 7.2 0 110 14.4 7.2 7.2 0 010-14.4zm0 2.4a4.8 4.8 0 100 9.6 4.8 4.8 0 000-9.6z"/>
      </svg>
    )
  },
  {
    id: 'zapier',
    name: 'Zapier',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zm5.978 12.695l-3.282 3.282a1 1 0 01-1.414 0L12 14.695l-1.282 1.282a1 1 0 01-1.414 0l-3.282-3.282a1 1 0 010-1.414L9.304 8l-3.282-3.282a1 1 0 010-1.414l3.282-3.282a1 1 0 011.414 0L12 1.304l1.282-1.282a1 1 0 011.414 0l3.282 3.282a1 1 0 010 1.414L14.696 8l3.282 3.282a1 1 0 010 1.413z"/>
      </svg>
    )
  },
  {
    id: 'make',
    name: 'Make',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>
    )
  },
  {
    id: 'rest',
    name: 'REST API',
    icon: <Webhook className="w-5 h-5" />
  },
]

// Sidebar navigation
const sidebarNav = [
  {
    title: 'Getting Started',
    items: [
      { title: 'Introduction', href: '#introduction' },
      { title: 'Quick Start', href: '#quick-start' },
    ],
  },
  {
    title: 'SDKs',
    items: [
      { title: 'Python SDK', href: '#python-sdk' },
      { title: 'TypeScript SDK', href: '#typescript-sdk' },
    ],
  },
  {
    title: 'Framework Integrations',
    items: [
      { title: 'CrewAI', href: '#crewai' },
      { title: 'LangChain', href: '#langchain' },
      { title: 'AutoGen', href: '#autogen' },
      { title: 'Vercel AI SDK', href: '#vercelai' },
    ],
  },
  {
    title: 'Coordination Intelligence',
    items: [
      { title: 'Overview', href: '#coordination-overview' },
      { title: 'Issues Detection', href: '#issues-detection' },
      { title: 'ML Suggestions', href: '#ml-suggestions' },
      { title: 'Pattern Learning', href: '#pattern-learning' },
    ],
  },
  {
    title: 'Core Concepts',
    items: [
      { title: 'Agents', href: '#agents' },
      { title: 'Traces', href: '#traces' },
      { title: 'Tests', href: '#tests' },
    ],
  },
  {
    title: 'API Reference',
    items: [
      { title: 'Authentication', href: '#authentication' },
      { title: 'Agents API', href: '#agents-api' },
      { title: 'Traces API', href: '#traces-api' },
      { title: 'Coordination API', href: '#coordination-api' },
      { title: 'Webhooks', href: '#webhooks' },
    ],
  },
]

export default function DocsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('python')

  return (
    <div className="min-h-screen bg-black">
      <Navbar />

      <div className="flex pt-20">
        {/* Sidebar */}
        <aside
          className={cn(
            'fixed md:sticky top-20 left-0 z-40 w-64 h-[calc(100vh-5rem)] bg-black border-r border-white/10 overflow-y-auto transition-transform md:translate-x-0',
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          )}
        >
          <nav className="p-4 space-y-6">
            <button
              className="md:hidden w-full mb-4 p-2 text-gray-400 hover:text-white flex items-center gap-2 border border-white/10 rounded-lg"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-4 h-4" />
              <span className="text-sm">Close menu</span>
            </button>
            {sidebarNav.map((section) => (
              <div key={section.title}>
                <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                  {section.title}
                </h4>
                <ul className="space-y-1">
                  {section.items.map((item) => (
                    <li key={item.href}>
                      <a
                        href={item.href}
                        className="block px-2 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-colors"
                      >
                        {item.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </aside>

        {/* Mobile menu button */}
        <button
          className="md:hidden fixed bottom-4 left-4 z-50 p-3 bg-purple-600 text-white rounded-full shadow-lg"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Main content */}
        <main className="flex-1 max-w-4xl mx-auto px-6 py-8">
          <div className="prose prose-invert max-w-none">
            
            {/* Header */}
            <section id="introduction" className="mb-16">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-purple-500/20 rounded-lg">
                  <Book className="w-6 h-6 text-purple-400" />
                </div>
                <h1 className="text-3xl font-medium text-white m-0">OverseeX Documentation</h1>
              </div>
              <p className="text-gray-400 text-lg">
                Complete guide to integrating OverseeX for AI agent monitoring, testing, and security.
              </p>
            </section>

            {/* Platform Tabs */}
            <section className="mb-12">
              <h2 className="text-xl font-medium text-white mb-6">Choose Your Platform</h2>
              <div className="flex flex-wrap gap-2 p-1 bg-white/5 rounded-xl">
                {platformTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all',
                      activeTab === tab.id
                        ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/25'
                        : 'text-gray-400 hover:text-white hover:bg-white/10'
                    )}
                  >
                    {tab.icon}
                    {tab.name}
                  </button>
                ))}
              </div>
            </section>

            {/* Dynamic Content Based on Tab */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {activeTab === 'python' && <PythonContent />}
                {activeTab === 'typescript' && <TypeScriptContent />}
                {activeTab === 'javascript' && <JavaScriptContent />}
                {activeTab === 'crewai' && <CrewAIContent />}
                {activeTab === 'langchain' && <LangChainContent />}
                {activeTab === 'autogen' && <AutoGenContent />}
                {activeTab === 'vercelai' && <VercelAIContent />}
                {activeTab === 'n8n' && <N8nContent />}
                {activeTab === 'zapier' && <ZapierContent />}
                {activeTab === 'make' && <MakeContent />}
                {activeTab === 'rest' && <RestApiContent />}
              </motion.div>
            </AnimatePresence>

            {/* Footer */}
            <footer className="pt-8 mt-16 border-t border-white/10">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <p>© 2026 OverseeX. All rights reserved.</p>
                <div className="flex items-center gap-4">
                  <a href="https://github.com/overseex" target="_blank" className="hover:text-white transition-colors flex items-center gap-1">
                    GitHub <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </footer>
          </div>
        </main>
      </div>
    </div>
  )
}

// Python Content
function PythonContent() {
  return (
    <div className="space-y-12">
      <section id="quick-start">
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <svg className="w-8 h-8 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z"/>
          </svg>
          Python SDK Installation
        </h2>
        <p className="text-gray-400 mb-6">Install the OverseeX Python SDK using pip or poetry.</p>
        
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using pip:</h4>
            <CodeBlock code="pip install overseex" language="bash" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using poetry:</h4>
            <CodeBlock code="poetry add overseex" language="bash" />
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Quick Start</h3>
        <CodeBlock
          code={`from overseex import OverseeX

# Initialize the client
client = OverseeX(api_key="your-api-key")

# Create an agent
agent = client.create_agent(
    name="My AI Agent",
    description="Customer support chatbot"
)

# Start tracing
with client.trace(agent_id=agent.id) as trace:
    # Your AI agent logic here
    response = your_ai_function(user_input)
    
    # Log tool calls
    trace.log_tool_call(
        tool="openai",
        input=user_input,
        output=response
    )

# Generate tests automatically
client.generate_tests(agent_id=agent.id, limit=10)`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">LangChain Integration</h3>
        <CodeBlock
          code={`from overseex import OverseeX
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

# Initialize OverseeX
oversee = OverseeX(api_key="your-api-key")

# Wrap your LangChain agent
llm = ChatOpenAI()
agent = initialize_agent(tools, llm)

# Use with tracing
with oversee.trace(agent_id="agent_123") as trace:
    result = agent.run("What's the weather?")
    # All tool calls automatically logged`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">CrewAI Integration</h3>
        <CodeBlock
          code={`from overseex import OverseeX
from crewai import Agent, Task, Crew

oversee = OverseeX(api_key="your-api-key")

# Create CrewAI agents
researcher = Agent(name="Researcher", role="...")
writer = Agent(name="Writer", role="...")

# Wrap crew execution
with oversee.trace(agent_id="crew_123") as trace:
    crew = Crew(agents=[researcher, writer], tasks=[...])
    result = crew.kickoff()
    # All interactions traced`}
          language="python"
        />
      </section>
    </div>
  )
}

// JavaScript Content
function JavaScriptContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <svg className="w-8 h-8 text-yellow-400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M0 0h24v24H0V0zm22.034 18.276c-.175-1.095-.888-2.015-3.003-2.873-.736-.345-1.554-.585-1.797-1.14-.091-.33-.105-.51-.046-.705.15-.646.915-.84 1.515-.66.39.12.75.42.976.9 1.034-.676 1.034-.676 1.755-1.125-.27-.42-.404-.601-.586-.78-.63-.705-1.469-1.065-2.834-1.034l-.705.089c-.676.165-1.32.525-1.71 1.005-1.14 1.291-.811 3.541.569 4.471 1.365 1.02 3.361 1.244 3.616 2.205.24 1.17-.87 1.545-1.966 1.41-.811-.18-1.26-.586-1.755-1.336l-1.83 1.051c.21.48.45.689.81 1.109 1.74 1.756 6.09 1.666 6.871-1.004.029-.09.24-.705.074-1.65l.046.067zm-8.983-7.245h-2.248c0 1.938-.009 3.864-.009 5.805 0 1.232.063 2.363-.138 2.711-.33.689-1.18.601-1.566.48-.396-.196-.597-.466-.83-.855-.063-.105-.11-.196-.127-.196l-1.825 1.125c.305.63.75 1.172 1.324 1.517.855.51 2.004.675 3.207.405.783-.226 1.458-.691 1.811-1.411.51-.93.402-2.07.397-3.346.012-2.054 0-4.109 0-6.179l.004-.056z"/>
          </svg>
          JavaScript SDK Installation
        </h2>
        
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using npm:</h4>
            <CodeBlock code="npm install overseex" language="bash" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using pnpm:</h4>
            <CodeBlock code="pnpm add overseex" language="bash" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using yarn:</h4>
            <CodeBlock code="yarn add overseex" language="bash" />
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Quick Start</h3>
        <CodeBlock
          code={`import { OverseeX } from 'overseex';

// Initialize
const client = new OverseeX({
  apiKey: process.env.OVERSEEX_API_KEY
});

// Create an agent
const agent = await client.createAgent({
  name: 'My AI Agent',
  description: 'Customer support bot'
});

// Wrap your function for automatic tracing
const tracedAgent = client.wrap(myAgentFunction);

// Run with tracing
const result = await tracedAgent.run('Hello, world!');

// Generate tests from traces
await client.generateTests({
  agentId: agent.id,
  limit: 10
});`}
          language="typescript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">OpenAI Integration</h3>
        <CodeBlock
          code={`import { OverseeX, traceOpenAI } from 'overseex';
import OpenAI from 'openai';

const oversee = new OverseeX({ apiKey: 'your-key' });
const openai = traceOpenAI(new OpenAI(), oversee);

// All OpenAI calls are now automatically traced
const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello!' }]
});`}
          language="typescript"
        />
      </section>
    </div>
  )
}

// TypeScript Content
function TypeScriptContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <svg className="w-8 h-8 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M1.125 0C.502 0 0 .502 0 1.125v21.75C0 23.498.502 24 1.125 24h21.75c.623 0 1.125-.502 1.125-1.125V1.125C24 .502 23.498 0 22.875 0zm17.363 9.75c.612 0 1.154.037 1.627.111a6.38 6.38 0 0 1 1.306.34v2.458a3.95 3.95 0 0 0-.643-.361 5.093 5.093 0 0 0-.717-.26 5.453 5.453 0 0 0-1.426-.2c-.3 0-.573.028-.819.086a2.1 2.1 0 0 0-.623.242c-.17.104-.3.229-.393.374a.888.888 0 0 0-.14.49c0 .196.053.373.156.529.104.156.252.304.443.444s.423.276.696.41c.273.135.582.274.926.416.47.197.892.407 1.266.628.374.222.695.473.963.753.268.279.472.598.614.957.142.359.214.776.214 1.253 0 .657-.125 1.21-.373 1.656a3.033 3.033 0 0 1-1.012 1.085 4.38 4.38 0 0 1-1.487.596c-.566.12-1.163.18-1.79.18a9.916 9.916 0 0 1-1.84-.164 5.544 5.544 0 0 1-1.512-.493v-2.63a5.033 5.033 0 0 0 3.237 1.2c.333 0 .624-.03.872-.09.249-.06.456-.144.623-.25.166-.108.29-.234.373-.38a1.023 1.023 0 0 0-.074-1.089 2.12 2.12 0 0 0-.537-.5 5.597 5.597 0 0 0-.807-.444 27.72 27.72 0 0 0-1.007-.436c-.918-.383-1.602-.852-2.053-1.405-.45-.553-.676-1.222-.676-2.005 0-.614.123-1.141.369-1.582.246-.441.58-.804 1.004-1.089a4.494 4.494 0 0 1 1.47-.629 7.536 7.536 0 0 1 1.77-.201zm-15.113.188h9.563v2.166H9.506v9.646H6.789v-9.646H3.375z"/>
          </svg>
          TypeScript SDK Installation
        </h2>
        <p className="text-gray-400 mb-6">Install the OverseeX TypeScript SDK for full type safety and multi-agent coordination intelligence.</p>

        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using npm:</h4>
            <CodeBlock code="npm install overseex" language="bash" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using pnpm:</h4>
            <CodeBlock code="pnpm add overseex" language="bash" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Using yarn:</h4>
            <CodeBlock code="yarn add overseex" language="bash" />
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Quick Start</h3>
        <CodeBlock
          code={`import { OverseeX } from 'overseex';

// Initialize with full type safety
const client = new OverseeX({
  apiKey: process.env.OVERSEEX_API_KEY!,
  debug: true
});

// Create an agent
const agent = await client.createAgent({
  name: 'My AI Agent',
  description: 'Customer support bot'
});

// Wrap your function for automatic tracing
const tracedAgent = client.wrap(myAgentFunction, {
  name: 'customer-support',
  captureInput: true,
  captureOutput: true
});

// Run with tracing
const result = await tracedAgent('Hello, world!');`}
          language="typescript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Multi-Agent Coordination</h3>
        <p className="text-gray-400 mb-4">Track handoffs, detect state drift, and analyze coordination patterns between agents.</p>
        <CodeBlock
          code={`import { OverseeX } from 'overseex';

const client = new OverseeX({ apiKey: 'your-key' });

// Create a span for multi-agent workflow
const span = client.createSpan('multi-agent-workflow', {
  tags: ['multi-agent', 'coordination']
});

// Record agent handoffs
span.recordHandoff({
  fromAgent: 'researcher',
  toAgent: 'writer',
  reason: 'Research complete, passing to writer',
  context: { topic: 'AI safety', sources: 5 }
});

// Record LLM calls
span.recordLLMCall({
  model: 'gpt-4',
  prompt: 'Write an article about AI safety',
  response: 'Article content...',
  tokens: 1500,
  durationMs: 2500
});

// Record tool calls
span.recordToolCall({
  tool: 'web_search',
  input: 'AI safety research papers 2026',
  output: '10 results found',
  durationMs: 800
});

span.setStatus('success');
span.end();`}
          language="typescript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Coordination Intelligence API</h3>
        <p className="text-gray-400 mb-4">Access ML-powered coordination analysis, issues, and suggestions.</p>
        <CodeBlock
          code={`// Get coordination issues
const issues = await client.coordination.listIssues({
  severity: 'high',
  status: 'open'
});

// Get ML-powered suggestions
const suggestions = await client.coordination.listSuggestions({
  minConfidence: 0.8
});

// Provide feedback to improve suggestions
await client.coordination.provideFeedback(
  suggestionId,
  'approved',
  'This fix resolved the handoff timeout issue'
);

// Get learned patterns
const patterns = await client.coordination.listPatterns({
  issueType: 'handoff_failure',
  isActive: true
});

// Analyze traces for coordination issues
const analysis = await client.coordination.analyze(
  ['trace-id-1', 'trace-id-2'],
  true // auto-create issues
);`}
          language="typescript"
        />
      </section>
    </div>
  )
}

// CrewAI Content
function CrewAIContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <div className="p-1.5 bg-green-500/20 rounded-lg">
            <svg className="w-6 h-6 text-green-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
          </div>
          CrewAI Integration
        </h2>
        <p className="text-gray-400 mb-6">
          Zero-config auto-instrumentation for CrewAI multi-agent systems. Automatically capture agent handoffs, task execution, and coordination patterns.
        </p>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Installation</h3>
        <CodeBlock code="pip install overseex[crewai]" language="bash" />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Basic Usage</h3>
        <CodeBlock
          code={`from overseex import OverseeX
from overseex.integrations.crewai import CrewAIInstrumentation
from crewai import Agent, Task, Crew

# Initialize OverseeX
client = OverseeX(api_key="your-api-key")

# Enable CrewAI instrumentation
instrumentation = CrewAIInstrumentation(client)
instrumentation.instrument()

# Create your CrewAI agents as usual
researcher = Agent(
    role="Research Analyst",
    goal="Find and analyze relevant information",
    backstory="Expert researcher with attention to detail"
)

writer = Agent(
    role="Content Writer",
    goal="Create compelling content from research",
    backstory="Experienced writer who crafts engaging narratives"
)

# Define tasks
research_task = Task(
    description="Research AI safety trends for 2026",
    agent=researcher
)

writing_task = Task(
    description="Write a comprehensive article based on research",
    agent=writer
)

# Create and run crew - everything is automatically traced!
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task]
)

result = crew.kickoff()
# All agent interactions, handoffs, and tool calls are captured`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">What Gets Captured</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <ul className="space-y-3 text-gray-300">
            <li className="flex items-start gap-3">
              <span className="text-green-400 mt-1">-</span>
              <span><strong>Agent Handoffs:</strong> Track when tasks are delegated between agents</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-400 mt-1">-</span>
              <span><strong>Task Execution:</strong> Monitor task start, completion, and duration</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-400 mt-1">-</span>
              <span><strong>Tool Calls:</strong> Log all tool invocations with inputs/outputs</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-400 mt-1">-</span>
              <span><strong>LLM Calls:</strong> Capture prompts, responses, tokens, and costs</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-400 mt-1">-</span>
              <span><strong>Coordination Issues:</strong> Detect state drift, handoff failures, broken assumptions</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-400 mt-1">-</span>
              <span><strong>Agent Flow:</strong> Visualize the complete execution graph</span>
            </li>
          </ul>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Advanced Configuration</h3>
        <CodeBlock
          code={`from overseex.integrations.crewai import CrewAIInstrumentation

# Configure instrumentation options
instrumentation = CrewAIInstrumentation(
    client,
    capture_prompts=True,      # Log full prompts (disable for privacy)
    capture_outputs=True,      # Log task outputs
    trace_tool_calls=True,     # Trace individual tool calls
    detect_coordination_issues=True,  # Enable ML coordination analysis
    auto_create_issues=True    # Automatically create issues for failures
)

instrumentation.instrument()

# Run your crew...

# Clean up when done
instrumentation.uninstrument()`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">View in Dashboard</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <pre className="text-sm text-gray-300 font-mono">
{`Dashboard Features:

- Agent Workflow Visualization (React Flow graph)
  [Researcher] ---> [Writer] ---> [Editor]
       |              |
       v              v
   [Web Search]   [Formatter]

- Coordination Issues Panel
  - State drift detected between Researcher -> Writer
  - Handoff timeout on task delegation
  - Missing context in agent handoff

- ML Suggestions
  - "Add retry logic for web search tool (87% confidence)"
  - "Increase timeout for research tasks (92% confidence)"`}
          </pre>
        </div>
      </section>
    </div>
  )
}

// LangChain Content
function LangChainContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <div className="p-1.5 bg-emerald-500/20 rounded-lg">
            <svg className="w-6 h-6 text-emerald-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M13.5 2c-5.621 0-10.211 4.443-10.475 10h-3.025l5 6.625 5-6.625h-2.975c.257-3.351 3.06-6 6.475-6 3.584 0 6.5 2.916 6.5 6.5s-2.916 6.5-6.5 6.5c-1.863 0-3.542-.793-4.728-2.053l-2.427 3.216c1.877 1.754 4.389 2.837 7.155 2.837 5.79 0 10.5-4.71 10.5-10.5s-4.71-10.5-10.5-10.5z"/>
            </svg>
          </div>
          LangChain Integration
        </h2>
        <p className="text-gray-400 mb-6">
          Full integration with LangChain and LangGraph. Trace chains, agents, and state graphs with automatic coordination analysis.
        </p>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Installation</h3>
        <CodeBlock code="pip install overseex[langchain]" language="bash" />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Callback Handler</h3>
        <CodeBlock
          code={`from overseex import OverseeX
from overseex.integrations.langchain import OverseeXCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool

# Initialize OverseeX callback handler
client = OverseeX(api_key="your-api-key")
callback = OverseeXCallbackHandler(
    client=client,
    agent_id="langchain-agent",
    trace_llm_calls=True,
    trace_tool_calls=True,
    trace_chain_calls=True
)

# Create your LangChain agent with the callback
llm = ChatOpenAI(callbacks=[callback])

tools = [
    Tool(name="Search", func=search_func, description="Search the web"),
    Tool(name="Calculator", func=calc_func, description="Do math")
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="chat-conversational-react-description",
    callbacks=[callback]
)

# All interactions are automatically traced
result = agent.run("What is the population of Tokyo times 2?")`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">LangGraph State Graph Monitoring</h3>
        <CodeBlock
          code={`from overseex.integrations.langchain import OverseeXGraphMonitor
from langgraph.graph import StateGraph
from typing import TypedDict

# Define your state
class AgentState(TypedDict):
    messages: list
    next_agent: str

# Create LangGraph
graph = StateGraph(AgentState)
graph.add_node("researcher", researcher_node)
graph.add_node("writer", writer_node)
graph.add_edge("researcher", "writer")

# Wrap with OverseeX monitoring
monitor = OverseeXGraphMonitor(
    client=client,
    agent_id="langgraph-workflow"
)

# Monitor graph execution
compiled_graph = graph.compile()
monitored_graph = monitor.wrap_graph(compiled_graph)

# Run with full state tracking
result = monitored_graph.invoke({
    "messages": ["Write about AI"],
    "next_agent": "researcher"
})

# Captures:
# - State transitions between nodes
# - Node execution times
# - State drift detection
# - Handoff patterns`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Tracer Integration</h3>
        <CodeBlock
          code={`from overseex.integrations.langchain import OverseeXTracer
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Create tracer for detailed tracing
tracer = OverseeXTracer(
    client=client,
    agent_id="chain-tracer",
    project_name="my-langchain-project"
)

# Use with any chain
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a blog post about {topic}"
)

chain = LLMChain(
    llm=ChatOpenAI(),
    prompt=prompt,
    callbacks=[tracer]
)

# Execution is fully traced
result = chain.run(topic="machine learning")`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">What Gets Captured</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <ul className="space-y-3 text-gray-300">
            <li className="flex items-start gap-3">
              <span className="text-emerald-400 mt-1">-</span>
              <span><strong>Chain Execution:</strong> Full chain runs with inputs/outputs</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-400 mt-1">-</span>
              <span><strong>LLM Calls:</strong> All model invocations with prompts, responses, tokens</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-400 mt-1">-</span>
              <span><strong>Tool Usage:</strong> Tool calls with inputs, outputs, and timing</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-400 mt-1">-</span>
              <span><strong>Agent Steps:</strong> Each agent reasoning step and action</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-400 mt-1">-</span>
              <span><strong>State Graphs:</strong> LangGraph node transitions and state changes</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-400 mt-1">-</span>
              <span><strong>Memory Updates:</strong> Conversation memory changes</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-400 mt-1">-</span>
              <span><strong>Errors:</strong> Exceptions with full stack traces</span>
            </li>
          </ul>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Coordination Analysis</h3>
        <p className="text-gray-400 mb-4">Automatically detect coordination issues in your LangChain workflows:</p>
        <CodeBlock
          code={`# Enable coordination analysis
callback = OverseeXCallbackHandler(
    client=client,
    agent_id="my-agent",
    detect_coordination_issues=True,  # Enable ML analysis
    auto_suggestions=True              # Get fix suggestions
)

# After running your agent, check for issues
issues = client.coordination.list_issues(
    agent_id="my-agent",
    status="open"
)

for issue in issues:
    print(f"Issue: {issue.issue_type}")
    print(f"Severity: {issue.severity}")
    print(f"Description: {issue.description}")

    # Get suggestions for this issue
    suggestions = client.coordination.list_suggestions(
        issue_id=issue.id
    )
    for suggestion in suggestions:
        print(f"Suggestion: {suggestion.description}")
        print(f"Confidence: {suggestion.confidence}%")`}
          language="python"
        />
      </section>
    </div>
  )
}

// AutoGen Content
function AutoGenContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <div className="p-1.5 bg-blue-500/20 rounded-lg">
            <svg className="w-6 h-6 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
          </div>
          Microsoft AutoGen Integration
        </h2>
        <p className="text-gray-400 mb-6">
          Auto-instrumentation for Microsoft AutoGen multi-agent conversations. Capture agent interactions, function calls, and coordination patterns.
        </p>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Installation</h3>
        <CodeBlock code="pip install overseex-autogen" language="bash" />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Basic Usage</h3>
        <CodeBlock
          code={`from overseex_autogen import monitor_autogen, AutoGenMonitor
from autogen import AssistantAgent, UserProxyAgent
import autogen

# Initialize OverseeX monitoring
monitor = AutoGenMonitor(
    api_key="your-api-key",
    agent_id="autogen-workflow"
)

# Use as context manager for automatic tracing
with monitor_autogen(api_key="your-api-key", agent_id="my-autogen"):
    # Configure AutoGen
    config_list = [{"model": "gpt-4", "api_key": "..."}]

    # Create agents
    assistant = AssistantAgent(
        name="assistant",
        llm_config={"config_list": config_list}
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        code_execution_config={"work_dir": "coding"}
    )

    # Start conversation - all interactions are traced!
    user_proxy.initiate_chat(
        assistant,
        message="Write a Python function to calculate fibonacci numbers"
    )
    # Traces capture: messages, function calls, code execution, handoffs`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Callback Handler</h3>
        <CodeBlock
          code={`from overseex_autogen import OverseeXAutoGenCallback

# Create callback for fine-grained control
callback = OverseeXAutoGenCallback(
    api_key="your-api-key",
    agent_id="autogen-agent",
    capture_code_execution=True,
    capture_function_calls=True,
    detect_coordination_issues=True
)

# Register with AutoGen agents
assistant = AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list},
    # AutoGen will call our callback on events
)

# Access captured data
callback.get_conversation_history()
callback.get_function_calls()
callback.get_coordination_issues()`}
          language="python"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">What Gets Captured</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <ul className="space-y-3 text-gray-300">
            <li className="flex items-start gap-3">
              <span className="text-blue-400 mt-1">-</span>
              <span><strong>Agent Messages:</strong> All messages exchanged between agents</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-400 mt-1">-</span>
              <span><strong>Function Calls:</strong> Tool/function invocations with parameters and results</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-400 mt-1">-</span>
              <span><strong>Code Execution:</strong> Generated code and execution results</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-400 mt-1">-</span>
              <span><strong>Agent Handoffs:</strong> Conversation flow between agents</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-400 mt-1">-</span>
              <span><strong>LLM Calls:</strong> Model invocations with tokens and timing</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-400 mt-1">-</span>
              <span><strong>Errors:</strong> Exceptions and failure states</span>
            </li>
          </ul>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Group Chat Monitoring</h3>
        <CodeBlock
          code={`from autogen import GroupChat, GroupChatManager

# Create multiple agents
coder = AssistantAgent(name="coder", ...)
reviewer = AssistantAgent(name="reviewer", ...)
tester = AssistantAgent(name="tester", ...)

# Group chat with automatic tracing
with monitor_autogen(api_key="key", agent_id="group-chat"):
    groupchat = GroupChat(
        agents=[user_proxy, coder, reviewer, tester],
        messages=[],
        max_round=10
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={"config_list": config_list}
    )

    # All agent interactions in the group are traced
    user_proxy.initiate_chat(
        manager,
        message="Create a REST API with tests"
    )

    # View in dashboard:
    # - Agent participation graph
    # - Message flow timeline
    # - Coordination issues detected`}
          language="python"
        />
      </section>
    </div>
  )
}

// Vercel AI SDK Content
function VercelAIContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <div className="p-1.5 bg-gray-500/20 rounded-lg">
            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M24 22.525H0l12-21.05 12 21.05z"/>
            </svg>
          </div>
          Vercel AI SDK Integration
        </h2>
        <p className="text-gray-400 mb-6">
          Automatic telemetry integration for Vercel AI SDK. Track AI streams, tool calls, and multi-step generations.
        </p>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Installation</h3>
        <CodeBlock code="npm install @overseex/vercel-ai" language="bash" />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Basic Usage</h3>
        <CodeBlock
          code={`import { OverseeXTelemetry, withOverseeXTelemetry } from '@overseex/vercel-ai';
import { generateText, streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

// Create telemetry instance
const telemetry = new OverseeXTelemetry({
  apiKey: process.env.OVERSEEX_API_KEY!,
  agentId: 'vercel-ai-agent'
});

// Use with generateText
const result = await generateText({
  model: openai('gpt-4'),
  prompt: 'Write a haiku about programming',
  experimental_telemetry: telemetry.getConfig()
});

// Use with streamText
const stream = await streamText({
  model: openai('gpt-4'),
  prompt: 'Explain quantum computing',
  experimental_telemetry: telemetry.getConfig()
});

// All calls are automatically traced with:
// - Model used
// - Input/output tokens
// - Duration
// - Streaming chunks (for streamText)`}
          language="typescript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Tool Calls Tracing</h3>
        <CodeBlock
          code={`import { generateText, tool } from 'ai';
import { z } from 'zod';

const result = await generateText({
  model: openai('gpt-4'),
  tools: {
    weather: tool({
      description: 'Get the weather in a location',
      parameters: z.object({
        location: z.string().describe('The city name'),
      }),
      execute: async ({ location }) => {
        // Tool execution is automatically traced
        return { temp: 72, condition: 'sunny' };
      },
    }),
    calculator: tool({
      description: 'Perform calculations',
      parameters: z.object({
        expression: z.string(),
      }),
      execute: async ({ expression }) => {
        return { result: eval(expression) };
      },
    }),
  },
  prompt: 'What is the weather in NYC and what is 25 * 4?',
  experimental_telemetry: telemetry.getConfig()
});

// Traces include:
// - Each tool call with input/output
// - Tool execution duration
// - LLM reasoning steps`}
          language="typescript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Multi-Step Generations</h3>
        <CodeBlock
          code={`import { generateText } from 'ai';

// Multi-step tool calling with full tracing
const result = await generateText({
  model: openai('gpt-4'),
  tools: { weather, search, calculator },
  maxSteps: 5, // Allow multiple tool use rounds
  prompt: 'Research and summarize weather patterns',
  experimental_telemetry: telemetry.getConfig()
});

// Each step is traced:
// Step 1: LLM decides to call 'search' tool
// Step 2: Search results returned
// Step 3: LLM decides to call 'weather' tool
// Step 4: Weather data returned
// Step 5: LLM generates final summary

// View full execution flow in OverseeX dashboard`}
          language="typescript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Next.js Integration</h3>
        <CodeBlock
          code={`// app/api/chat/route.ts
import { OverseeXTelemetry } from '@overseex/vercel-ai';
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

const telemetry = new OverseeXTelemetry({
  apiKey: process.env.OVERSEEX_API_KEY!,
  agentId: 'nextjs-chat'
});

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4'),
    messages,
    experimental_telemetry: telemetry.getConfig({
      metadata: {
        userId: 'user-123',
        conversationId: 'conv-456'
      }
    })
  });

  return result.toDataStreamResponse();
}

// Traces include custom metadata for filtering`}
          language="typescript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">What Gets Captured</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <ul className="space-y-3 text-gray-300">
            <li className="flex items-start gap-3">
              <span className="text-gray-400 mt-1">-</span>
              <span><strong>Model Calls:</strong> All LLM invocations with model info</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-gray-400 mt-1">-</span>
              <span><strong>Token Usage:</strong> Input/output/total tokens per call</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-gray-400 mt-1">-</span>
              <span><strong>Tool Executions:</strong> Tool calls with parameters and results</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-gray-400 mt-1">-</span>
              <span><strong>Streaming Data:</strong> Chunk timing for streamed responses</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-gray-400 mt-1">-</span>
              <span><strong>Multi-Step Flows:</strong> Complete execution graphs</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-gray-400 mt-1">-</span>
              <span><strong>Errors:</strong> Failed generations with context</span>
            </li>
          </ul>
        </div>
      </section>
    </div>
  )
}

// n8n Content
function N8nContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <div className="p-1.5 bg-orange-500/20 rounded-lg">
            <svg className="w-6 h-6 text-orange-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 4.8a7.2 7.2 0 110 14.4 7.2 7.2 0 010-14.4zm0 2.4a4.8 4.8 0 100 9.6 4.8 4.8 0 000-9.6z"/>
            </svg>
          </div>
          n8n Integration
        </h2>
        <p className="text-gray-400 mb-6">
          Integrate OverseeX with n8n workflows using HTTP Request nodes for AI agent monitoring.
        </p>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Step 1: Start a Trace</h3>
        <p className="text-gray-400 mb-4">Add an HTTP Request node before your AI call:</p>
        <CodeBlock
          code={`// n8n HTTP Request Node Configuration
Method: POST
URL: https://api.overseex.com/api/v1/traces

Headers:
  Authorization: Bearer YOUR_API_KEY
  Content-Type: application/json

Body (JSON):
{
  "agent_id": "your-agent-id",
  "trace_data": {
    "input": "{{ $json.user_query }}",
    "start_time": "{{ new Date().toISOString() }}",
    "metadata": {
      "workflow": "n8n",
      "node": "Start Trace"
    }
  }
}`}
          language="javascript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Step 2: Record AI Call</h3>
        <p className="text-gray-400 mb-4">After your OpenAI/Claude node, log the response:</p>
        <CodeBlock
          code={`// HTTP Request: Record Tool Call
Method: POST
URL: https://api.overseex.com/api/v1/traces/{{ $json.trace_id }}/tool-calls

Body:
{
  "tool": "openai",
  "input": "{{ $node['Webhook'].json.query }}",
  "output": "{{ $node['OpenAI'].json.response }}",
  "duration_ms": 1200
}`}
          language="javascript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Complete Workflow</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <pre className="text-sm text-gray-300 font-mono">
{`┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Webhook   │────▶│  Start Trace │────▶│   OpenAI    │────▶│  End Trace   │
│   Trigger   │     │  (OverseeX)  │     │    Call     │     │  (OverseeX)  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘

Benefits:
✅ All AI interactions logged
✅ Error monitoring & alerts
✅ Performance analytics
✅ Automatic test generation`}
          </pre>
        </div>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Receive Webhooks in n8n</h3>
        <p className="text-gray-400 mb-4">Configure OverseeX to send events to your n8n webhook:</p>
        <CodeBlock
          code={`// n8n Webhook Trigger receives events like:
{
  "event": "agent.trace_completed",
  "timestamp": "2026-01-25T10:30:00Z",
  "data": {
    "trace_id": "trace_abc123",
    "agent_id": "agent_xyz",
    "status": "success",
    "duration_ms": 1500
  }
}

// Then process with Switch node:
- trace_completed → Log to database
- agent.error → Send Slack alert
- test_failed → Create ticket`}
          language="javascript"
        />
      </section>
    </div>
  )
}

// Zapier Content
function ZapierContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <div className="p-1.5 bg-orange-500/20 rounded-lg">
            <svg className="w-6 h-6 text-orange-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zm5.978 12.695l-3.282 3.282a1 1 0 01-1.414 0L12 14.695l-1.282 1.282a1 1 0 01-1.414 0l-3.282-3.282a1 1 0 010-1.414L9.304 8l-3.282-3.282a1 1 0 010-1.414l3.282-3.282a1 1 0 011.414 0L12 1.304l1.282-1.282a1 1 0 011.414 0l3.282 3.282a1 1 0 010 1.414L14.696 8l3.282 3.282a1 1 0 010 1.413z"/>
            </svg>
          </div>
          Zapier Integration
        </h2>
        <p className="text-gray-400 mb-6">
          Use Webhooks by Zapier to send AI agent data to OverseeX.
        </p>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Create a Zap</h3>
        <CodeBlock
          code={`// Zapier Webhook Action Configuration

Action: Webhooks by Zapier → Custom Request

Method: POST
URL: https://api.overseex.com/api/v1/traces

Headers:
  Authorization: Bearer YOUR_API_KEY
  Content-Type: application/json

Data (JSON):
{
  "agent_id": "your-agent-id",
  "trace_data": {
    "input": "{{trigger_data.input}}",
    "output": "{{ai_response}}",
    "status": "success",
    "timestamp": "{{zap_meta_human_now}}"
  }
}`}
          language="javascript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Example Zap Flow</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <pre className="text-sm text-gray-300 font-mono">
{`1. Trigger: New ChatGPT conversation (OpenAI)
2. Action: Webhook POST to OverseeX (create trace)
3. Action: Process response
4. Action: Webhook PATCH to OverseeX (complete trace)

Or for monitoring:
1. Trigger: Webhook from OverseeX (agent.error)
2. Action: Send Slack message
3. Action: Create Jira ticket`}
          </pre>
        </div>
      </section>
    </div>
  )
}

// Make Content  
function MakeContent() {
  return (
    <div className="space-y-12">
      <section>
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <div className="p-1.5 bg-purple-500/20 rounded-lg">
            <svg className="w-6 h-6 text-purple-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          Make (Integromat) Integration
        </h2>
        <p className="text-gray-400 mb-6">
          Add HTTP modules to your Make scenarios for OverseeX integration.
        </p>
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">HTTP Module Setup</h3>
        <CodeBlock
          code={`// Make HTTP Module Configuration

Module: HTTP → Make a request

URL: https://api.overseex.com/api/v1/traces
Method: POST

Headers:
  - Authorization: Bearer YOUR_API_KEY
  - Content-Type: application/json

Body type: Raw
Content type: JSON (application/json)

Request content:
{
  "agent_id": "{{agent_id}}",
  "trace_data": {
    "input": "{{1.input}}",
    "output": "{{2.output}}",
    "tool_calls": [
      {
        "tool": "{{1.tool_name}}",
        "response": "{{2.response}}"
      }
    ]
  }
}`}
          language="javascript"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Scenario Example</h3>
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <pre className="text-sm text-gray-300 font-mono">
{`Scenario: AI Agent Monitoring

[Webhook] → [HTTP: Create Trace] → [OpenAI] → [HTTP: Log Tool] → [HTTP: Complete Trace] → [Response]

Modules:
1. Webhooks → Custom webhook (receives user request)
2. HTTP → POST /api/v1/traces (start trace)
3. OpenAI → Create chat completion
4. HTTP → POST /api/v1/traces/{id}/tool-calls
5. HTTP → PATCH /api/v1/traces/{id} (complete)
6. Webhooks → Webhook response`}
          </pre>
        </div>
      </section>
    </div>
  )
}

// REST API Content
function RestApiContent() {
  return (
    <div className="space-y-12">
      <section id="authentication">
        <h2 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
          <Key className="w-6 h-6 text-purple-400" />
          Authentication
        </h2>
        <p className="text-gray-400 mb-6">
          All API requests require a Bearer token in the Authorization header.
        </p>
        <CodeBlock
          code={`curl -X GET "https://api.overseex.com/api/v1/agents" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`}
          language="bash"
        />
      </section>

      <section id="agents-api">
        <h3 className="text-xl font-medium text-white mb-4">Create Agent</h3>
        <CodeBlock
          code={`POST /api/v1/agents
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "name": "My AI Agent",
  "description": "Customer support chatbot",
  "config": {
    "model": "gpt-4",
    "temperature": 0.7
  }
}

Response:
{
  "id": "agent_abc123",
  "name": "My AI Agent",
  "created_at": "2026-01-25T10:00:00Z"
}`}
          language="json"
        />
      </section>

      <section id="traces-api">
        <h3 className="text-xl font-medium text-white mb-4">Create Trace</h3>
        <CodeBlock
          code={`POST /api/v1/traces
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "agent_id": "agent_abc123",
  "trace_data": {
    "input": "User question here",
    "output": "AI response here",
    "status": "success",
    "tool_calls": [
      {
        "tool": "web_search",
        "input": "search query",
        "output": "search results"
      }
    ]
  }
}`}
          language="json"
        />
      </section>

      <section id="webhooks">
        <h3 className="text-xl font-medium text-white mb-4">Webhook Events</h3>
        <p className="text-gray-400 mb-4">Configure webhooks to receive real-time events:</p>
        <CodeBlock
          code={`Available Events:
- agent.trace_completed  - Trace finished successfully
- agent.trace_failed     - Trace ended with error
- agent.test_passed      - Automated test passed
- agent.test_failed      - Automated test failed
- agent.health_warning   - Health check warning
- agent.health_critical  - Health check critical

Webhook Payload:
{
  "event": "agent.trace_completed",
  "timestamp": "2026-01-25T10:30:00Z",
  "data": {
    "trace_id": "trace_abc123",
    "agent_id": "agent_xyz",
    "status": "success",
    "duration_ms": 1500
  }
}

Headers:
X-OverseeX-Signature: sha256=...
X-OverseeX-Event: agent.trace_completed
X-OverseeX-Delivery: delivery_12345`}
          language="yaml"
        />
      </section>

      <section>
        <h3 className="text-xl font-medium text-white mb-4">Verify Webhook Signature</h3>
        <CodeBlock
          code={`import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

# Usage
is_valid = verify_webhook(
    request.body,
    request.headers.get("X-OverseeX-Signature"),
    os.environ["WEBHOOK_SECRET"]
)`}
          language="python"
        />
      </section>
    </div>
  )
}

'use client'

import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

interface CodeBlockProps {
  code: string | Record<string, string>
  language?: string
  showLineNumbers?: boolean
}

// Token-based syntax highlighting to avoid regex conflicts
type Token = {
  type: 'keyword' | 'string' | 'comment' | 'number' | 'decorator' | 'function' | 'builtin' | 'variable' | 'operator' | 'type' | 'plain'
  value: string
}

export function CodeBlock({ code, language = 'bash', showLineNumbers = false }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState<string>('')

  // Handle multi-tab code blocks
  const isMultiTab = typeof code === 'object'
  const tabs = isMultiTab ? Object.keys(code) : []
  const currentTab = activeTab || tabs[0]
  const currentCode = isMultiTab ? code[currentTab] : code

  const handleCopy = () => {
    navigator.clipboard.writeText(currentCode as string)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Escape HTML characters
  const escapeHtml = (str: string) => {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }

  // Color mapping for token types
  const tokenColors: Record<Token['type'], string> = {
    keyword: 'text-rose-400',
    string: 'text-emerald-400',
    comment: 'text-gray-500',
    number: 'text-amber-400',
    decorator: 'text-violet-400',
    function: 'text-yellow-400',
    builtin: 'text-cyan-400',
    variable: 'text-amber-400',
    operator: 'text-gray-400',
    type: 'text-cyan-400',
    plain: ''
  }

  // Tokenize Python code
  const tokenizePython = (code: string): Token[] => {
    const tokens: Token[] = []
    const keywords = new Set(['from', 'import', 'def', 'class', 'return', 'if', 'else', 'elif', 'try', 'except', 'finally', 'with', 'as', 'for', 'while', 'break', 'continue', 'pass', 'async', 'await', 'yield', 'lambda', 'raise', 'assert', 'global', 'nonlocal', 'in', 'is', 'not', 'and', 'or', 'True', 'False', 'None'])
    const builtins = new Set(['print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'type', 'isinstance', 'enumerate', 'zip', 'open', 'self', 'cls'])
    
    let i = 0
    while (i < code.length) {
      // Comments
      if (code[i] === '#') {
        let end = code.indexOf('\n', i)
        if (end === -1) end = code.length
        tokens.push({ type: 'comment', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Strings (double or single quotes, including multi-line)
      if (code[i] === '"' || code[i] === "'") {
        const quote = code[i]
        const isTriple = code.slice(i, i + 3) === quote.repeat(3)
        const endQuote = isTriple ? quote.repeat(3) : quote
        const startPos = i
        i += isTriple ? 3 : 1
        
        while (i < code.length) {
          if (code[i] === '\\' && i + 1 < code.length) {
            i += 2
            continue
          }
          if (code.slice(i, i + endQuote.length) === endQuote) {
            i += endQuote.length
            break
          }
          i++
        }
        tokens.push({ type: 'string', value: code.slice(startPos, i) })
        continue
      }
      
      // Decorators
      if (code[i] === '@') {
        let end = i + 1
        while (end < code.length && /[a-zA-Z0-9_.]/.test(code[end])) end++
        tokens.push({ type: 'decorator', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Numbers
      if (/[0-9]/.test(code[i])) {
        let end = i
        while (end < code.length && /[0-9.]/.test(code[end])) end++
        tokens.push({ type: 'number', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Identifiers and keywords
      if (/[a-zA-Z_]/.test(code[i])) {
        let end = i
        while (end < code.length && /[a-zA-Z0-9_]/.test(code[end])) end++
        const word = code.slice(i, end)
        
        // Check if it's a function call
        let afterWord = end
        while (afterWord < code.length && /\s/.test(code[afterWord])) afterWord++
        const isFunction = code[afterWord] === '('
        
        if (keywords.has(word)) {
          tokens.push({ type: 'keyword', value: word })
        } else if (builtins.has(word)) {
          tokens.push({ type: 'builtin', value: word })
        } else if (isFunction) {
          tokens.push({ type: 'function', value: word })
        } else {
          tokens.push({ type: 'plain', value: word })
        }
        i = end
        continue
      }
      
      // Everything else (whitespace, operators, etc.)
      tokens.push({ type: 'plain', value: code[i] })
      i++
    }
    
    return tokens
  }

  // Tokenize bash/shell code
  const tokenizeBash = (code: string): Token[] => {
    const tokens: Token[] = []
    const commands = new Set(['curl', 'pip', 'pnpm', 'npm', 'yarn', 'install', 'create', 'add', 'run', 'uvicorn', 'python', 'cd', 'mkdir', 'source', 'export', 'echo', 'git', 'docker'])
    
    let i = 0
    while (i < code.length) {
      // Comments
      if (code[i] === '#') {
        let end = code.indexOf('\n', i)
        if (end === -1) end = code.length
        tokens.push({ type: 'comment', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Strings
      if (code[i] === '"' || code[i] === "'") {
        const quote = code[i]
        const startPos = i
        i++
        while (i < code.length && code[i] !== quote) {
          if (code[i] === '\\' && i + 1 < code.length) i++
          i++
        }
        if (i < code.length) i++
        tokens.push({ type: 'string', value: code.slice(startPos, i) })
        continue
      }
      
      // Shell variables ($VAR)
      if (code[i] === '$') {
        let end = i + 1
        while (end < code.length && /[a-zA-Z0-9_]/.test(code[end])) end++
        if (end > i + 1) {
          tokens.push({ type: 'variable', value: code.slice(i, end) })
          i = end
          continue
        }
      }
      
      // Flags (--flag or -f)
      if (code[i] === '-' && i + 1 < code.length && /[a-zA-Z-]/.test(code[i + 1])) {
        let end = i + 1
        while (end < code.length && /[a-zA-Z0-9-]/.test(code[end])) end++
        tokens.push({ type: 'builtin', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Commands/identifiers
      if (/[a-zA-Z_]/.test(code[i])) {
        let end = i
        while (end < code.length && /[a-zA-Z0-9_]/.test(code[end])) end++
        const word = code.slice(i, end)
        
        if (commands.has(word)) {
          tokens.push({ type: 'keyword', value: word })
        } else {
          tokens.push({ type: 'plain', value: word })
        }
        i = end
        continue
      }
      
      // URLs
      if (code.slice(i, i + 7) === 'http://' || code.slice(i, i + 8) === 'https://') {
        let end = i
        while (end < code.length && !/\s/.test(code[end])) end++
        tokens.push({ type: 'string', value: code.slice(i, end) })
        i = end
        continue
      }
      
      tokens.push({ type: 'plain', value: code[i] })
      i++
    }
    
    return tokens
  }

  // Tokenize JavaScript/TypeScript code
  const tokenizeJS = (code: string): Token[] => {
    const tokens: Token[] = []
    const keywords = new Set(['const', 'let', 'var', 'function', 'async', 'await', 'return', 'if', 'else', 'try', 'catch', 'finally', 'new', 'import', 'from', 'export', 'default', 'class', 'extends', 'implements', 'interface', 'type', 'enum', 'for', 'while', 'do', 'break', 'continue', 'switch', 'case', 'throw', 'true', 'false', 'null', 'undefined', 'this'])
    const builtins = new Set(['console', 'window', 'document', 'process', 'Array', 'Object', 'String', 'Number', 'Boolean', 'Promise'])
    
    let i = 0
    while (i < code.length) {
      // Single-line comments
      if (code.slice(i, i + 2) === '//') {
        let end = code.indexOf('\n', i)
        if (end === -1) end = code.length
        tokens.push({ type: 'comment', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Multi-line comments
      if (code.slice(i, i + 2) === '/*') {
        let end = code.indexOf('*/', i + 2)
        if (end === -1) end = code.length
        else end += 2
        tokens.push({ type: 'comment', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Template literals
      if (code[i] === '`') {
        const startPos = i
        i++
        while (i < code.length && code[i] !== '`') {
          if (code[i] === '\\' && i + 1 < code.length) i++
          i++
        }
        if (i < code.length) i++
        tokens.push({ type: 'string', value: code.slice(startPos, i) })
        continue
      }
      
      // Strings
      if (code[i] === '"' || code[i] === "'") {
        const quote = code[i]
        const startPos = i
        i++
        while (i < code.length && code[i] !== quote && code[i] !== '\n') {
          if (code[i] === '\\' && i + 1 < code.length) i++
          i++
        }
        if (i < code.length && code[i] === quote) i++
        tokens.push({ type: 'string', value: code.slice(startPos, i) })
        continue
      }
      
      // Numbers
      if (/[0-9]/.test(code[i])) {
        let end = i
        while (end < code.length && /[0-9.]/.test(code[end])) end++
        tokens.push({ type: 'number', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Identifiers and keywords
      if (/[a-zA-Z_$]/.test(code[i])) {
        let end = i
        while (end < code.length && /[a-zA-Z0-9_$]/.test(code[end])) end++
        const word = code.slice(i, end)
        
        let afterWord = end
        while (afterWord < code.length && /\s/.test(code[afterWord])) afterWord++
        const isFunction = code[afterWord] === '('
        
        if (keywords.has(word)) {
          tokens.push({ type: 'keyword', value: word })
        } else if (builtins.has(word)) {
          tokens.push({ type: 'builtin', value: word })
        } else if (isFunction) {
          tokens.push({ type: 'function', value: word })
        } else {
          tokens.push({ type: 'plain', value: word })
        }
        i = end
        continue
      }
      
      tokens.push({ type: 'plain', value: code[i] })
      i++
    }
    
    return tokens
  }

  // Tokenize JSON code
  const tokenizeJSON = (code: string): Token[] => {
    const tokens: Token[] = []
    
    let i = 0
    let expectingKey = true
    
    while (i < code.length) {
      // Strings
      if (code[i] === '"') {
        const startPos = i
        i++
        while (i < code.length && code[i] !== '"') {
          if (code[i] === '\\' && i + 1 < code.length) i++
          i++
        }
        if (i < code.length) i++
        const value = code.slice(startPos, i)
        
        // Check if this is a key (followed by :)
        let afterString = i
        while (afterString < code.length && /\s/.test(code[afterString])) afterString++
        const isKey = code[afterString] === ':'
        
        tokens.push({ type: isKey ? 'type' : 'string', value })
        continue
      }
      
      // Numbers
      if (/[-0-9]/.test(code[i])) {
        let end = i
        if (code[end] === '-') end++
        while (end < code.length && /[0-9.eE+-]/.test(code[end])) end++
        tokens.push({ type: 'number', value: code.slice(i, end) })
        i = end
        continue
      }
      
      // Booleans and null
      if (code.slice(i, i + 4) === 'true') {
        tokens.push({ type: 'keyword', value: 'true' })
        i += 4
        continue
      }
      if (code.slice(i, i + 5) === 'false') {
        tokens.push({ type: 'keyword', value: 'false' })
        i += 5
        continue
      }
      if (code.slice(i, i + 4) === 'null') {
        tokens.push({ type: 'keyword', value: 'null' })
        i += 4
        continue
      }
      
      tokens.push({ type: 'plain', value: code[i] })
      i++
    }
    
    return tokens
  }

  // Convert tokens to HTML
  const tokensToHtml = (tokens: Token[]): string => {
    return tokens.map(token => {
      const escaped = escapeHtml(token.value)
      const color = tokenColors[token.type]
      if (color) {
        return `<span class="${color}">${escaped}</span>`
      }
      return escaped
    }).join('')
  }

  // Main highlight function
  const highlightSyntax = (code: string, lang: string): string => {
    if (lang === 'bash' || lang === 'shell') {
      return tokensToHtml(tokenizeBash(code))
    }
    if (lang === 'python') {
      return tokensToHtml(tokenizePython(code))
    }
    if (lang === 'javascript' || lang === 'typescript') {
      return tokensToHtml(tokenizeJS(code))
    }
    if (lang === 'json') {
      return tokensToHtml(tokenizeJSON(code))
    }
    return escapeHtml(code)
  }

  return (
    <div className="relative group my-4">
      {/* Tabs for multi-language code blocks */}
      {isMultiTab && (
        <div className="flex gap-2 mb-2 border-b border-white/10">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium transition-all ${
                (activeTab || tabs[0]) === tab
                  ? 'text-violet-400 border-b-2 border-violet-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      )}

      {/* Code block with darker background */}
      <div className="relative rounded-xl overflow-hidden bg-gradient-to-br from-gray-950 to-black border border-white/10 shadow-2xl">
        {/* Always visible copy button */}
        <div className="absolute top-3 right-3 z-10">
          <button
            onClick={handleCopy}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 transition-all"
            aria-label="Copy code"
          >
            {copied ? (
              <Check className="w-4 h-4 text-emerald-400" />
            ) : (
              <Copy className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>

        <pre className="p-6 overflow-x-auto text-sm leading-relaxed">
          <code
            className="text-gray-300 font-mono"
            dangerouslySetInnerHTML={{
              __html: highlightSyntax(currentCode as string, language)
            }}
          />
        </pre>
      </div>
    </div>
  )
}

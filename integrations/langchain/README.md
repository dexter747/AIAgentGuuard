# OverseeX LangChain Integration

Automatic trace capture for [LangChain](https://langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/) applications with multi-agent handoff tracking.

## Installation

```bash
pip install overseex-langchain

# For LangGraph support
pip install overseex-langchain[langgraph]
```

## Quick Start

### Basic Callback Handler

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from overseex_langchain import OverseeXCallbackHandler

# Create callback handler
handler = OverseeXCallbackHandler(
    api_key="ox_live_your_key",
    agent_name="My LangChain App"
)

# Create chain with callback
prompt = ChatPromptTemplate.from_template("Write a short poem about {topic}")
llm = ChatOpenAI(model="gpt-4")

chain = prompt | llm

# Run chain - automatically traced!
result = chain.invoke(
    {"topic": "artificial intelligence"},
    config={"callbacks": [handler]}
)
print(result.content)
```

### Auto-Instrumentation (Zero Code Changes)

```python
from overseex_langchain import OverseeXCallbackHandler, install_hooks

# Install hooks globally - all LangChain calls will be traced
handler = OverseeXCallbackHandler(api_key="ox_live_your_key")
install_hooks(handler)

# Now any LangChain code is automatically traced
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
result = llm.invoke("Hello!")  # Automatically traced!
```

### LangGraph Multi-Agent Workflows

```python
from langgraph.graph import StateGraph, END
from overseex_langchain import LangGraphMonitor

# Create monitor
monitor = LangGraphMonitor(api_key="ox_live_your_key")

# Build your graph
from typing import TypedDict

class AgentState(TypedDict):
    messages: list
    next: str

graph = StateGraph(AgentState)

# Add nodes (agents)
graph.add_node("researcher", researcher_agent)
graph.add_node("writer", writer_agent)
graph.add_node("reviewer", reviewer_agent)

# Add edges (handoffs)
graph.add_edge("researcher", "writer")
graph.add_edge("writer", "reviewer")
graph.add_edge("reviewer", END)

# Compile and wrap with monitoring
app = graph.compile()
monitored_app = monitor.wrap_graph(app)

# Run - handoffs automatically tracked!
result = monitored_app.invoke({"messages": ["Research AI trends"]})
```

## Features

- **Automatic agent registration** - Agents auto-registered in OverseeX
- **LLM call tracking** - Capture prompts, responses, tokens, latency
- **Chain execution monitoring** - Track full chain execution flow
- **Tool usage tracking** - Monitor which tools are called
- **Retrieval monitoring** - Track vector DB queries
- **Multi-agent handoffs** - Detect and visualize agent transitions
- **LangGraph support** - Full support for stateful multi-agent graphs
- **Error capture** - Automatic error tracking
- **Cost estimation** - Approximate API costs per run

## Usage Examples

### With LCEL Chains

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from overseex_langchain import OverseeXCallbackHandler

handler = OverseeXCallbackHandler(api_key="ox_live_...")

prompt = ChatPromptTemplate.from_template("Explain {topic} simply")
llm = ChatOpenAI()
parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke(
    {"topic": "quantum computing"},
    config={"callbacks": [handler]}
)
```

### With Agents

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.tools import Tool
from overseex_langchain import OverseeXCallbackHandler

handler = OverseeXCallbackHandler(api_key="ox_live_...")

# Define tools
tools = [
    Tool(
        name="Calculator",
        func=lambda x: eval(x),
        description="Useful for math calculations"
    )
]

# Create agent
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Run agent - tools and LLM calls automatically traced
result = agent_executor.invoke(
    {"input": "What is 25 * 4 + 10?"},
    config={"callbacks": [handler]}
)
```

### With RAG

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from overseex_langchain import OverseeXCallbackHandler

handler = OverseeXCallbackHandler(
    api_key="ox_live_...",
    capture_retrieval=True
)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_texts(
    ["AI is transforming industries..."],
    embeddings
)
retriever = vectorstore.as_retriever()

# Create RAG chain
prompt = ChatPromptTemplate.from_template(
    "Answer based on context: {context}\n\nQuestion: {question}"
)
llm = ChatOpenAI()

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
)

result = chain.invoke("What is AI?", config={"callbacks": [handler]})
```

### Multi-Agent Handoff Tracking

```python
from overseex_langchain import OverseeXCallbackHandler

handler = OverseeXCallbackHandler(api_key="ox_live_...")

# Register agents for better tracking
handler.register_agent("researcher", "Research Agent", role="research")
handler.register_agent("writer", "Writer Agent", role="content")
handler.register_agent("reviewer", "Review Agent", role="qa")

# Manually record handoffs in custom orchestration
handler.record_handoff(
    from_agent="researcher",
    to_agent="writer",
    reason="Research complete, ready for writing",
    context={"research_results": [...]}
)
```

## Configuration

```python
handler = OverseeXCallbackHandler(
    api_key="ox_live_your_key",
    agent_id="langchain-123",       # Optional: use existing agent
    agent_name="My App",            # Used for auto-registration
    base_url="https://api.overseex.com",
    capture_llm_calls=True,         # Capture LLM requests/responses
    capture_tool_calls=True,        # Capture tool executions
    capture_retrieval=True,         # Capture retrieval queries
    capture_handoffs=True,          # Detect agent handoffs
    auto_register_agent=True,       # Auto-register if agent_id is None
    tags=["production", "rag"],     # Tags for filtering
    metadata={"version": "1.0"}     # Extra metadata
)
```

## What Gets Captured

### LLM Calls

```json
{
    "llm_calls": [
        {
            "model": "gpt-4",
            "prompts": ["Write a poem about AI"],
            "responses": ["Artificial minds that think and learn..."],
            "duration_ms": 1250,
            "token_count": 156,
            "cost": 0.0094
        }
    ]
}
```

### Agent Handoffs

```json
{
    "handoffs": [
        {
            "from_agent": "researcher",
            "to_agent": "writer",
            "timestamp": 1737645123.45,
            "reason": "Research complete",
            "context": {"topics": ["AI", "ML"]}
        }
    ],
    "agent_flow": ["researcher", "writer", "reviewer"]
}
```

### Tool Calls

```json
{
    "tool_calls": [
        {
            "tool": "Calculator",
            "input": "25 * 4 + 10",
            "output": "110",
            "duration_ms": 5
        }
    ]
}
```

## Dashboard Integration

All captured data appears in OverseeX dashboard:

- **Coordination Graph** - Visualize agent handoffs and flow
- **Timeline view** - See LLM calls in sequence
- **Cost tracking** - Monitor API spending
- **Token usage** - Optimize prompt efficiency
- **Tool usage** - Track which tools are used
- **Retrieval analysis** - See what documents are retrieved
- **Error tracking** - Identify failure patterns

## Support

- Docs: https://docs.overseex.com/integrations/langchain
- Issues: https://github.com/overseex/overseex-langchain/issues

## License

MIT

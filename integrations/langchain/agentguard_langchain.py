"""
AgentGuard LangChain Integration

Automatic trace capture for LangChain applications via callbacks.

Install:
    pip install agentguard-langchain

Usage:
    from agentguard_langchain import AgentGuardCallbackHandler
    from langchain.chains import LLMChain
    from langchain.llms import OpenAI
    
    # Create callback handler
    handler = AgentGuardCallbackHandler(
        api_key="ag_live_your_key",
        agent_id="langchain-agent-123"
    )
    
    # Use with any LangChain component
    chain = LLMChain(llm=OpenAI(), callbacks=[handler])
    result = chain.run("What is AI?")
    
    # Traces automatically sent to AgentGuard!
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
import time

try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
except ImportError:
    raise ImportError(
        "LangChain is not installed. Install it with: pip install langchain"
    )

try:
    from agentguard import AgentGuard
except ImportError:
    raise ImportError(
        "AgentGuard SDK is not installed. Install it with: pip install agentguard"
    )


class AgentGuardCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler that captures execution traces.
    
    Captures:
    - LLM calls and responses
    - Chain executions
    - Tool uses
    - Agent actions
    - Retrieval queries
    - Errors and retries
    """
    
    def __init__(
        self,
        api_key: str,
        agent_id: Optional[str] = None,
        agent_name: str = "LangChain Agent",
        base_url: str = "http://localhost:8000",
        capture_llm_calls: bool = True,
        capture_tool_calls: bool = True,
        capture_retrieval: bool = True,
        auto_register_agent: bool = True
    ):
        """
        Initialize AgentGuard callback handler.
        
        Args:
            api_key: AgentGuard API key
            agent_id: AgentGuard agent ID (will be created if None)
            agent_name: Agent name for auto-registration
            base_url: AgentGuard API base URL
            capture_llm_calls: Capture LLM requests/responses
            capture_tool_calls: Capture tool executions
            capture_retrieval: Capture retrieval queries
            auto_register_agent: Auto-register agent if agent_id is None
        """
        self.client = AgentGuard(api_key=api_key, base_url=base_url)
        self.agent_name = agent_name
        self.capture_llm_calls = capture_llm_calls
        self.capture_tool_calls = capture_tool_calls
        self.capture_retrieval = capture_retrieval
        
        # Auto-register agent
        if agent_id is None and auto_register_agent:
            try:
                agent = self.client.create_agent(
                    name=agent_name,
                    endpoint_url="langchain://local",
                    description="LangChain agent with automatic tracing"
                )
                self.agent_id = agent.id
                print(f"✅ Registered agent: {agent_name} ({agent.id})")
            except Exception as e:
                print(f"⚠️ Failed to register agent: {e}")
                self.agent_id = "langchain-default"
        else:
            self.agent_id = agent_id or "langchain-default"
        
        # Track active runs
        self.runs: Dict[UUID, Dict[str, Any]] = {}
        self.chain_start_times: Dict[UUID, float] = {}
        self.llm_calls: List[Dict[str, Any]] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.retrieval_queries: List[Dict[str, Any]] = []
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """Called when LLM starts running."""
        if not self.capture_llm_calls:
            return
        
        run_id = kwargs.get("run_id")
        self.runs[run_id] = {
            "type": "llm",
            "prompts": prompts,
            "start_time": time.time(),
            "model": serialized.get("name", "unknown")
        }
    
    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any
    ) -> None:
        """Called when LLM ends running."""
        if not self.capture_llm_calls:
            return
        
        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)
        
        # Extract token counts
        llm_output = response.llm_output or {}
        token_count = llm_output.get("token_usage", {}).get("total_tokens", 0)
        
        # Extract generated text
        generations = [
            [gen.text for gen in generation]
            for generation in response.generations
        ]
        
        self.llm_calls.append({
            "model": run_data["model"],
            "prompts": run_data["prompts"],
            "responses": generations,
            "duration_ms": duration_ms,
            "token_count": token_count,
            "timestamp": time.time()
        })
        
        del self.runs[run_id]
    
    def on_llm_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """Called when LLM errors."""
        run_id = kwargs.get("run_id")
        if run_id in self.runs:
            self.runs[run_id]["error"] = str(error)
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Called when chain starts running."""
        run_id = kwargs.get("run_id")
        self.chain_start_times[run_id] = time.time()
        self.runs[run_id] = {
            "type": "chain",
            "inputs": inputs,
            "start_time": time.time(),
            "chain_type": serialized.get("name", "unknown")
        }
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Called when chain ends running."""
        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)
        
        # Calculate total tokens from LLM calls
        total_tokens = sum(call.get("token_count", 0) for call in self.llm_calls)
        
        # Estimate cost (rough estimate: $0.002 per 1K tokens)
        cost = (total_tokens / 1000) * 0.002
        
        try:
            # Create trace
            trace = self.client.trace(
                agent_id=self.agent_id,
                input_data=run_data["inputs"],
                output_data=outputs,
                status="success",
                metadata={
                    "chain_type": run_data["chain_type"],
                    "llm_calls": self.llm_calls,
                    "tool_calls": self.tool_calls,
                    "retrieval_queries": self.retrieval_queries,
                },
                duration_ms=duration_ms,
                token_count=total_tokens,
                cost=cost
            )
            print(f"✅ Trace captured: {trace.id}")
        except Exception as e:
            print(f"⚠️ Failed to create trace: {e}")
        
        # Clean up
        del self.runs[run_id]
        if run_id in self.chain_start_times:
            del self.chain_start_times[run_id]
        self.llm_calls.clear()
        self.tool_calls.clear()
        self.retrieval_queries.clear()
    
    def on_chain_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """Called when chain errors."""
        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)
        
        try:
            # Create error trace
            trace = self.client.trace(
                agent_id=self.agent_id,
                input_data=run_data["inputs"],
                output_data={},
                status="error",
                error_message=str(error),
                metadata={
                    "chain_type": run_data["chain_type"],
                    "error_type": type(error).__name__,
                },
                duration_ms=duration_ms
            )
            print(f"❌ Error trace captured: {trace.id}")
        except Exception as e:
            print(f"⚠️ Failed to create error trace: {e}")
        
        # Clean up
        del self.runs[run_id]
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any
    ) -> None:
        """Called when tool starts running."""
        if not self.capture_tool_calls:
            return
        
        run_id = kwargs.get("run_id")
        self.runs[run_id] = {
            "type": "tool",
            "tool_name": serialized.get("name", "unknown"),
            "input": input_str,
            "start_time": time.time()
        }
    
    def on_tool_end(
        self,
        output: str,
        **kwargs: Any
    ) -> None:
        """Called when tool ends running."""
        if not self.capture_tool_calls:
            return
        
        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)
        
        self.tool_calls.append({
            "tool": run_data["tool_name"],
            "input": run_data["input"],
            "output": output[:500],  # Truncate long outputs
            "duration_ms": duration_ms,
            "timestamp": time.time()
        })
        
        del self.runs[run_id]
    
    def on_tool_error(
        self,
        error: Exception,
        **kwargs: Any
    ) -> None:
        """Called when tool errors."""
        run_id = kwargs.get("run_id")
        if run_id in self.runs:
            self.runs[run_id]["error"] = str(error)
    
    def on_agent_action(
        self,
        action: AgentAction,
        **kwargs: Any
    ) -> None:
        """Called when agent takes an action."""
        # Track agent actions as tool calls
        if self.capture_tool_calls:
            self.tool_calls.append({
                "tool": action.tool,
                "input": str(action.tool_input)[:500],
                "log": action.log[:500] if action.log else "",
                "timestamp": time.time()
            })
    
    def on_agent_finish(
        self,
        finish: AgentFinish,
        **kwargs: Any
    ) -> None:
        """Called when agent finishes."""
        # Track agent completion
        pass
    
    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        **kwargs: Any
    ) -> None:
        """Called when retriever starts."""
        if not self.capture_retrieval:
            return
        
        run_id = kwargs.get("run_id")
        self.runs[run_id] = {
            "type": "retrieval",
            "query": query,
            "start_time": time.time()
        }
    
    def on_retriever_end(
        self,
        documents: List[Any],
        **kwargs: Any
    ) -> None:
        """Called when retriever ends."""
        if not self.capture_retrieval:
            return
        
        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return
        
        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)
        
        self.retrieval_queries.append({
            "query": run_data["query"],
            "num_documents": len(documents),
            "documents": [doc.page_content[:200] for doc in documents[:3]],  # First 3 docs
            "duration_ms": duration_ms,
            "timestamp": time.time()
        })
        
        del self.runs[run_id]
    
    def close(self):
        """Close the AgentGuard client."""
        self.client.close()


__all__ = ["AgentGuardCallbackHandler"]

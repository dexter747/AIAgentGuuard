"""
LangChain Integration for AgentGuard
Production-ready callback handlers for automatic trace capture
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from uuid import UUID
import logging

try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object

from agentguard.client import AgentGuardClient
from agentguard.trace import Trace

logger = logging.getLogger(__name__)


class AgentGuardLangChainHandler(BaseCallbackHandler):
    """
    LangChain callback handler for AgentGuard
    
    Automatically captures:
    - LLM calls and responses
    - Tool executions
    - Agent actions
    - Chain executions
    - Errors and retries
    
    Usage:
        from agentguard.integrations.langchain import AgentGuardLangChainHandler
        from langchain.agents import AgentExecutor
        
        handler = AgentGuardLangChainHandler(
            api_key="your-api-key",
            agent_id="your-agent-id"
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            callbacks=[handler]
        )
        
        result = agent_executor.run("Your query")
    """
    
    def __init__(
        self,
        api_key: str,
        agent_id: str,
        base_url: Optional[str] = None,
        auto_send: bool = True
    ):
        """
        Initialize the AgentGuard LangChain handler
        
        Args:
            api_key: AgentGuard API key
            agent_id: AgentGuard agent ID
            base_url: Optional custom API base URL
            auto_send: Automatically send traces on completion (default: True)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. Install with: pip install langchain"
            )
        
        super().__init__()
        self.client = AgentGuardClient(api_key=api_key, base_url=base_url)
        self.agent_id = agent_id
        self.auto_send = auto_send
        
        # Track current execution
        self.current_trace: Optional[Trace] = None
        self.run_stack: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized AgentGuard LangChain handler for agent {agent_id}")
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """Run when LLM starts"""
        if not self.current_trace:
            self.current_trace = Trace(agent_id=self.agent_id)
            self.current_trace.start_time = datetime.utcnow()
            self.current_trace.trace_data = {
                "input": prompts[0] if prompts else "",
                "steps": [],
                "tool_calls": [],
                "llm_calls": []
            }
        
        # Record LLM call
        llm_call = {
            "type": "llm_start",
            "model": serialized.get("name", "unknown"),
            "prompts": prompts,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.current_trace.trace_data.setdefault("llm_calls", []).append(llm_call)
        
        logger.debug(f"LLM started: {serialized.get('name')}")
    
    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any
    ) -> None:
        """Run when LLM ends"""
        if not self.current_trace:
            return
        
        # Extract token usage
        token_usage = response.llm_output.get("token_usage", {}) if response.llm_output else {}
        
        # Record LLM completion
        llm_call = {
            "type": "llm_end",
            "generations": [
                [gen.text for gen in generations]
                for generations in response.generations
            ],
            "token_usage": token_usage,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.current_trace.trace_data.setdefault("llm_calls", []).append(llm_call)
        
        # Update token count
        if "total_tokens" in token_usage:
            self.current_trace.token_count = token_usage["total_tokens"]
        
        logger.debug(f"LLM completed: {token_usage.get('total_tokens', 0)} tokens")
    
    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any
    ) -> None:
        """Run when LLM errors"""
        if not self.current_trace:
            return
        
        # Record error
        error_info = {
            "type": "llm_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.current_trace.trace_data.setdefault("errors", []).append(error_info)
        self.current_trace.trace_data["status"] = "error"
        
        logger.error(f"LLM error: {error}")
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any
    ) -> None:
        """Run when tool starts"""
        if not self.current_trace:
            return
        
        tool_call = {
            "tool": serialized.get("name", "unknown"),
            "input": input_str,
            "start_time": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Add to pending tool calls
        self.run_stack.append(tool_call)
        
        logger.debug(f"Tool started: {serialized.get('name')}")
    
    def on_tool_end(
        self,
        output: str,
        **kwargs: Any
    ) -> None:
        """Run when tool ends"""
        if not self.current_trace or not self.run_stack:
            return
        
        # Complete the tool call
        tool_call = self.run_stack.pop()
        tool_call["output"] = output
        tool_call["end_time"] = datetime.utcnow().isoformat()
        
        # Add to trace
        self.current_trace.trace_data.setdefault("tool_calls", []).append(tool_call)
        
        logger.debug(f"Tool completed: {tool_call.get('tool')}")
    
    def on_tool_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any
    ) -> None:
        """Run when tool errors"""
        if not self.current_trace:
            return
        
        # Record tool error
        if self.run_stack:
            tool_call = self.run_stack.pop()
            tool_call["error"] = str(error)
            tool_call["error_type"] = type(error).__name__
            tool_call["end_time"] = datetime.utcnow().isoformat()
            
            self.current_trace.trace_data.setdefault("tool_calls", []).append(tool_call)
        
        # Add to errors
        error_info = {
            "type": "tool_error",
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.current_trace.trace_data.setdefault("errors", []).append(error_info)
        
        logger.error(f"Tool error: {error}")
    
    def on_agent_action(
        self,
        action: AgentAction,
        **kwargs: Any
    ) -> None:
        """Run when agent takes an action"""
        if not self.current_trace:
            return
        
        action_data = {
            "type": "agent_action",
            "tool": action.tool,
            "tool_input": action.tool_input,
            "log": action.log,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.current_trace.trace_data.setdefault("steps", []).append(action_data)
        
        logger.debug(f"Agent action: {action.tool}")
    
    def on_agent_finish(
        self,
        finish: AgentFinish,
        **kwargs: Any
    ) -> None:
        """Run when agent finishes"""
        if not self.current_trace:
            return
        
        # Record completion
        self.current_trace.trace_data["output"] = finish.return_values
        self.current_trace.trace_data.setdefault("status", "success")
        self.current_trace.end_time = datetime.utcnow()
        
        # Calculate duration
        if self.current_trace.start_time:
            duration = (self.current_trace.end_time - self.current_trace.start_time).total_seconds()
            self.current_trace.total_duration_ms = int(duration * 1000)
        
        # Send trace if auto_send enabled
        if self.auto_send:
            try:
                self.client.create_trace(
                    agent_id=self.agent_id,
                    trace_data=self.current_trace.trace_data,
                    status=self.current_trace.trace_data.get("status", "success"),
                    total_duration_ms=self.current_trace.total_duration_ms,
                    token_count=self.current_trace.token_count
                )
                logger.info(f"Trace sent to AgentGuard: {self.current_trace.total_duration_ms}ms")
            except Exception as e:
                logger.error(f"Failed to send trace: {e}")
        
        # Reset for next run
        self.current_trace = None
        self.run_stack = []
        
        logger.debug("Agent finished")
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Run when chain starts"""
        # Only initialize trace at the top-level chain
        if not self.current_trace and not self.run_stack:
            self.current_trace = Trace(agent_id=self.agent_id)
            self.current_trace.start_time = datetime.utcnow()
            
            # Extract input
            input_text = inputs.get("input", inputs.get("query", str(inputs)))
            
            self.current_trace.trace_data = {
                "input": input_text,
                "steps": [],
                "tool_calls": [],
                "llm_calls": [],
                "chain_type": serialized.get("name", "unknown")
            }
        
        logger.debug(f"Chain started: {serialized.get('name')}")
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Run when chain ends"""
        # Only process at top-level chain
        if self.current_trace and not self.run_stack:
            self.current_trace.trace_data["output"] = outputs
            self.current_trace.end_time = datetime.utcnow()
            
            # Calculate duration
            if self.current_trace.start_time:
                duration = (self.current_trace.end_time - self.current_trace.start_time).total_seconds()
                self.current_trace.total_duration_ms = int(duration * 1000)
            
            # Set status if not already set
            if "status" not in self.current_trace.trace_data:
                self.current_trace.trace_data["status"] = "success"
            
            # Send trace if auto_send enabled
            if self.auto_send:
                try:
                    self.client.create_trace(
                        agent_id=self.agent_id,
                        trace_data=self.current_trace.trace_data,
                        status=self.current_trace.trace_data.get("status", "success"),
                        total_duration_ms=self.current_trace.total_duration_ms,
                        token_count=self.current_trace.token_count
                    )
                    logger.info(f"Trace sent to AgentGuard: {self.current_trace.total_duration_ms}ms")
                except Exception as e:
                    logger.error(f"Failed to send trace: {e}")
            
            # Reset
            self.current_trace = None
        
        logger.debug("Chain ended")
    
    def on_chain_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any
    ) -> None:
        """Run when chain errors"""
        if not self.current_trace:
            return
        
        # Record error
        error_info = {
            "type": "chain_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.current_trace.trace_data.setdefault("errors", []).append(error_info)
        self.current_trace.trace_data["status"] = "error"
        self.current_trace.end_time = datetime.utcnow()
        
        # Calculate duration
        if self.current_trace.start_time:
            duration = (self.current_trace.end_time - self.current_trace.start_time).total_seconds()
            self.current_trace.total_duration_ms = int(duration * 1000)
        
        # Send trace if auto_send enabled
        if self.auto_send:
            try:
                self.client.create_trace(
                    agent_id=self.agent_id,
                    trace_data=self.current_trace.trace_data,
                    status="error",
                    total_duration_ms=self.current_trace.total_duration_ms,
                    token_count=self.current_trace.token_count
                )
                logger.info(f"Error trace sent to AgentGuard")
            except Exception as e:
                logger.error(f"Failed to send error trace: {e}")
        
        # Reset
        self.current_trace = None
        self.run_stack = []
        
        logger.error(f"Chain error: {error}")

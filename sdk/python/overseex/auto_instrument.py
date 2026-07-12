"""
AgentGuard Auto-Instrumentation Module

Provides automatic tracing for AI frameworks without manual code changes.
Supports: LangChain, CrewAI, OpenAI, Anthropic, and generic Python functions.

Usage:
    from agentguard import AgentGuard
    from agentguard.auto_instrument import auto_trace, instrument_framework
    
    ag = AgentGuard(api_key="ag_live_xxx")
    
    # Option 1: Decorator for any function
    @auto_trace(ag, agent_id="my-agent")
    def my_ai_function(prompt):
        return openai.chat.completions.create(...)
    
    # Option 2: Auto-instrument entire framework
    instrument_framework(ag, "langchain")  # or "openai", "anthropic", "crewai"
"""

import functools
import time
import sys
import json
import traceback
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime
from contextlib import contextmanager
import logging
import threading
import hashlib

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """
    Automatically detects which AI frameworks are installed and in use.
    """
    
    SUPPORTED_FRAMEWORKS = {
        "langchain": {
            "packages": ["langchain", "langchain_core", "langchain_openai"],
            "markers": ["LLMChain", "ChatOpenAI", "AgentExecutor", "RetrievalQA"],
        },
        "crewai": {
            "packages": ["crewai"],
            "markers": ["Crew", "Agent", "Task"],
        },
        "openai": {
            "packages": ["openai"],
            "markers": ["ChatCompletion", "Completion"],
        },
        "anthropic": {
            "packages": ["anthropic"],
            "markers": ["Anthropic", "Claude"],
        },
        "autogen": {
            "packages": ["autogen", "pyautogen"],
            "markers": ["AssistantAgent", "UserProxyAgent"],
        },
        "llamaindex": {
            "packages": ["llama_index"],
            "markers": ["VectorStoreIndex", "ServiceContext"],
        },
    }
    
    @classmethod
    def detect_installed_frameworks(cls) -> List[str]:
        """Detect which AI frameworks are installed."""
        installed = []
        for framework, info in cls.SUPPORTED_FRAMEWORKS.items():
            for package in info["packages"]:
                if package in sys.modules:
                    installed.append(framework)
                    break
                try:
                    __import__(package)
                    installed.append(framework)
                    break
                except ImportError:
                    continue
        return installed
    
    @classmethod
    def detect_framework_from_code(cls, obj: Any) -> Optional[str]:
        """Detect framework from an object instance."""
        obj_type = type(obj).__name__
        module = type(obj).__module__ if hasattr(type(obj), '__module__') else ""
        
        for framework, info in cls.SUPPORTED_FRAMEWORKS.items():
            # Check module name
            for package in info["packages"]:
                if package in module:
                    return framework
            # Check class name markers
            for marker in info["markers"]:
                if marker in obj_type:
                    return framework
        
        return None
    
    @classmethod
    def get_framework_info(cls, obj: Any) -> Dict[str, Any]:
        """Extract framework-specific information from an object."""
        framework = cls.detect_framework_from_code(obj)
        info = {
            "framework": framework or "unknown",
            "class_name": type(obj).__name__,
            "module": getattr(type(obj), '__module__', 'unknown'),
        }
        
        # Extract framework-specific metadata
        if framework == "langchain":
            info.update(cls._extract_langchain_info(obj))
        elif framework == "crewai":
            info.update(cls._extract_crewai_info(obj))
        elif framework == "openai":
            info.update(cls._extract_openai_info(obj))
        
        return info
    
    @staticmethod
    def _extract_langchain_info(obj: Any) -> Dict[str, Any]:
        """Extract LangChain-specific info."""
        info = {}
        if hasattr(obj, 'llm'):
            info['llm_type'] = type(obj.llm).__name__
        if hasattr(obj, 'memory'):
            info['has_memory'] = obj.memory is not None
        if hasattr(obj, 'tools'):
            info['tools'] = [t.name if hasattr(t, 'name') else str(t) for t in (obj.tools or [])]
        if hasattr(obj, 'verbose'):
            info['verbose'] = obj.verbose
        return info
    
    @staticmethod
    def _extract_crewai_info(obj: Any) -> Dict[str, Any]:
        """Extract CrewAI-specific info."""
        info = {}
        if hasattr(obj, 'agents'):
            info['agent_count'] = len(obj.agents)
            info['agent_roles'] = [a.role for a in obj.agents if hasattr(a, 'role')]
        if hasattr(obj, 'tasks'):
            info['task_count'] = len(obj.tasks)
        if hasattr(obj, 'role'):
            info['role'] = obj.role
        if hasattr(obj, 'goal'):
            info['goal'] = obj.goal
        return info
    
    @staticmethod
    def _extract_openai_info(obj: Any) -> Dict[str, Any]:
        """Extract OpenAI-specific info."""
        info = {}
        if hasattr(obj, 'model'):
            info['model'] = obj.model
        return info


class TraceContext:
    """
    Thread-local storage for trace context.
    Enables nested trace tracking and parent-child relationships.
    """
    _local = threading.local()
    
    @classmethod
    def get_current_trace_id(cls) -> Optional[str]:
        return getattr(cls._local, 'trace_id', None)
    
    @classmethod
    def set_current_trace_id(cls, trace_id: str):
        cls._local.trace_id = trace_id
    
    @classmethod
    def get_trace_stack(cls) -> List[str]:
        if not hasattr(cls._local, 'stack'):
            cls._local.stack = []
        return cls._local.stack
    
    @classmethod
    def push_trace(cls, trace_id: str):
        cls.get_trace_stack().append(trace_id)
        cls.set_current_trace_id(trace_id)
    
    @classmethod
    def pop_trace(cls) -> Optional[str]:
        stack = cls.get_trace_stack()
        if stack:
            popped = stack.pop()
            cls._local.trace_id = stack[-1] if stack else None
            return popped
        return None


def auto_trace(
    client,
    agent_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    capture_args: bool = True,
    capture_return: bool = True,
    capture_exceptions: bool = True,
    auto_detect_framework: bool = True,
    extract_token_count: bool = True,
    extract_cost: bool = True,
    custom_metadata: Optional[Dict[str, Any]] = None,
):
    """
    Decorator for automatic tracing of AI agent functions.
    
    Args:
        client: AgentGuard client instance
        agent_id: Agent ID (auto-generated if None)
        agent_name: Agent name for auto-registration
        capture_args: Capture function arguments
        capture_return: Capture return value
        capture_exceptions: Capture and trace exceptions
        auto_detect_framework: Auto-detect AI framework
        extract_token_count: Try to extract token count from response
        extract_cost: Try to calculate cost from usage
        custom_metadata: Additional metadata to include
    
    Example:
        @auto_trace(client, agent_name="CustomerSupport")
        def handle_query(user_input):
            return my_chain.run(user_input)
    """
    def decorator(func: Callable) -> Callable:
        # Auto-register agent if needed
        _agent_id = agent_id
        _agent_name = agent_name or func.__name__
        
        if _agent_id is None:
            try:
                agent = client.create_agent(
                    name=_agent_name,
                    endpoint_url=f"function://{func.__module__}.{func.__name__}",
                    description=func.__doc__ or f"Auto-instrumented function: {func.__name__}"
                )
                _agent_id = agent.id
                logger.info(f"✅ Auto-registered agent: {_agent_name} ({_agent_id})")
            except Exception as e:
                # Agent might already exist, generate deterministic ID
                _agent_id = hashlib.md5(f"{func.__module__}.{func.__name__}".encode()).hexdigest()[:12]
                logger.warning(f"Using fallback agent ID: {_agent_id}")
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = f"trace_{int(time.time() * 1000)}"
            TraceContext.push_trace(trace_id)
            
            # Prepare input data
            input_data = {}
            if capture_args:
                input_data = _serialize_args(args, kwargs, func)
            
            # Detect framework if requested
            framework_info = {}
            if auto_detect_framework and args:
                for arg in args:
                    detected = FrameworkDetector.detect_framework_from_code(arg)
                    if detected:
                        framework_info = FrameworkDetector.get_framework_info(arg)
                        break
            
            # Execute function
            output_data = {}
            status = "success"
            error_message = None
            token_count = None
            cost = None
            
            try:
                result = func(*args, **kwargs)
                
                if capture_return:
                    output_data = _serialize_output(result)
                
                # Extract token count and cost from response
                if extract_token_count:
                    token_count = _extract_tokens(result)
                if extract_cost:
                    cost = _calculate_cost(result, token_count)
                
                return result
                
            except Exception as e:
                status = "error"
                error_message = f"{type(e).__name__}: {str(e)}"
                if capture_exceptions:
                    output_data = {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                raise
                
            finally:
                duration_ms = int((time.time() - start_time) * 1000)
                TraceContext.pop_trace()
                
                # Build metadata
                metadata = {
                    "function": func.__name__,
                    "module": func.__module__,
                    **framework_info,
                    **(custom_metadata or {})
                }
                
                # Send trace
                try:
                    client.trace(
                        agent_id=_agent_id,
                        input_data=input_data,
                        output_data=output_data,
                        status=status,
                        error_message=error_message,
                        metadata=metadata,
                        duration_ms=duration_ms,
                        token_count=token_count,
                        cost=cost
                    )
                except Exception as trace_error:
                    logger.error(f"Failed to send trace: {trace_error}")
        
        # Store agent_id on wrapper for reference
        wrapper._agentguard_agent_id = _agent_id
        wrapper._agentguard_client = client
        
        return wrapper
    return decorator


@contextmanager
def trace_block(
    client,
    agent_id: str,
    name: str,
    input_data: Optional[Dict] = None,
    metadata: Optional[Dict] = None
):
    """
    Context manager for tracing a block of code.
    
    Example:
        with trace_block(client, "agent-123", "process_order", {"order_id": 123}):
            # Your code here
            result = process(order)
    """
    start_time = time.time()
    trace_id = f"trace_{int(time.time() * 1000)}"
    TraceContext.push_trace(trace_id)
    
    output_data = {}
    status = "success"
    error_message = None
    
    try:
        yield output_data  # Allow setting output_data["result"] = ...
    except Exception as e:
        status = "error"
        error_message = str(e)
        output_data["error"] = str(e)
        raise
    finally:
        duration_ms = int((time.time() - start_time) * 1000)
        TraceContext.pop_trace()
        
        try:
            client.trace(
                agent_id=agent_id,
                input_data=input_data or {},
                output_data=output_data,
                status=status,
                error_message=error_message,
                metadata={"block_name": name, **(metadata or {})},
                duration_ms=duration_ms
            )
        except Exception as trace_error:
            logger.error(f"Failed to send trace: {trace_error}")


class InstrumentedFramework:
    """
    Base class for framework instrumentation.
    Subclasses implement framework-specific patching.
    """
    
    def __init__(self, client, agent_prefix: str = ""):
        self.client = client
        self.agent_prefix = agent_prefix
        self._original_methods = {}
        self._is_patched = False
    
    def patch(self):
        """Apply framework instrumentation."""
        raise NotImplementedError
    
    def unpatch(self):
        """Remove framework instrumentation."""
        raise NotImplementedError


class OpenAIInstrumentation(InstrumentedFramework):
    """
    Automatic instrumentation for OpenAI SDK.
    
    Usage:
        instrument = OpenAIInstrumentation(client)
        instrument.patch()
        
        # All OpenAI calls are now traced automatically
        response = openai.chat.completions.create(...)
    """
    
    def patch(self):
        if self._is_patched:
            return
        
        try:
            import openai
        except ImportError:
            logger.warning("OpenAI not installed, skipping instrumentation")
            return
        
        # Patch chat completions
        if hasattr(openai, 'chat'):
            self._patch_chat_completions(openai)
        
        # Patch legacy completions if available
        if hasattr(openai, 'Completion'):
            self._patch_completions(openai)
        
        self._is_patched = True
        logger.info("✅ OpenAI instrumentation enabled")
    
    def _patch_chat_completions(self, openai):
        """Patch chat.completions.create"""
        original_create = openai.chat.completions.create
        self._original_methods['chat_completions_create'] = original_create
        
        client = self.client
        agent_prefix = self.agent_prefix
        
        def traced_create(*args, **kwargs):
            start_time = time.time()
            model = kwargs.get('model', 'unknown')
            messages = kwargs.get('messages', [])
            
            # Generate agent ID from model
            agent_id = f"{agent_prefix}openai-{model}".replace(".", "-")
            
            input_data = {
                "messages": messages,
                "model": model,
                "temperature": kwargs.get('temperature'),
                "max_tokens": kwargs.get('max_tokens'),
            }
            
            try:
                response = original_create(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Extract response data
                output_data = {}
                token_count = None
                cost = None
                
                if hasattr(response, 'choices') and response.choices:
                    output_data["content"] = response.choices[0].message.content
                    output_data["finish_reason"] = response.choices[0].finish_reason
                
                if hasattr(response, 'usage') and response.usage:
                    token_count = response.usage.total_tokens
                    # Estimate cost (GPT-4: ~$0.03/1K input, $0.06/1K output)
                    input_cost = (response.usage.prompt_tokens / 1000) * 0.03
                    output_cost = (response.usage.completion_tokens / 1000) * 0.06
                    cost = input_cost + output_cost
                
                # Send trace
                try:
                    client.trace(
                        agent_id=agent_id,
                        input_data=input_data,
                        output_data=output_data,
                        status="success",
                        metadata={
                            "framework": "openai",
                            "model": model,
                            "finish_reason": output_data.get("finish_reason"),
                        },
                        duration_ms=duration_ms,
                        token_count=token_count,
                        cost=cost
                    )
                except Exception as e:
                    logger.error(f"Failed to trace OpenAI call: {e}")
                
                return response
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                try:
                    client.trace(
                        agent_id=agent_id,
                        input_data=input_data,
                        output_data={"error": str(e)},
                        status="error",
                        error_message=str(e),
                        metadata={"framework": "openai", "model": model},
                        duration_ms=duration_ms
                    )
                except:
                    pass
                raise
        
        openai.chat.completions.create = traced_create
    
    def _patch_completions(self, openai):
        """Patch legacy Completion.create"""
        # Similar implementation for legacy API
        pass
    
    def unpatch(self):
        if not self._is_patched:
            return
        
        try:
            import openai
            if 'chat_completions_create' in self._original_methods:
                openai.chat.completions.create = self._original_methods['chat_completions_create']
        except ImportError:
            pass
        
        self._is_patched = False
        logger.info("OpenAI instrumentation disabled")


class AnthropicInstrumentation(InstrumentedFramework):
    """
    Automatic instrumentation for Anthropic SDK.
    """
    
    def patch(self):
        if self._is_patched:
            return
        
        try:
            import anthropic
        except ImportError:
            logger.warning("Anthropic not installed, skipping instrumentation")
            return
        
        # Store original
        original_messages_create = anthropic.Anthropic.messages.create
        self._original_methods['messages_create'] = original_messages_create
        
        client = self.client
        agent_prefix = self.agent_prefix
        
        def traced_create(self_anthropic, *args, **kwargs):
            start_time = time.time()
            model = kwargs.get('model', 'claude-3')
            messages = kwargs.get('messages', [])
            
            agent_id = f"{agent_prefix}anthropic-{model}".replace(".", "-")
            
            input_data = {
                "messages": messages,
                "model": model,
                "max_tokens": kwargs.get('max_tokens'),
            }
            
            try:
                response = original_messages_create(self_anthropic, *args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                output_data = {}
                token_count = None
                cost = None
                
                if hasattr(response, 'content') and response.content:
                    output_data["content"] = response.content[0].text
                
                if hasattr(response, 'usage'):
                    token_count = response.usage.input_tokens + response.usage.output_tokens
                    # Claude pricing estimate
                    cost = (response.usage.input_tokens / 1000) * 0.008 + \
                           (response.usage.output_tokens / 1000) * 0.024
                
                try:
                    client.trace(
                        agent_id=agent_id,
                        input_data=input_data,
                        output_data=output_data,
                        status="success",
                        metadata={"framework": "anthropic", "model": model},
                        duration_ms=duration_ms,
                        token_count=token_count,
                        cost=cost
                    )
                except Exception as e:
                    logger.error(f"Failed to trace Anthropic call: {e}")
                
                return response
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                try:
                    client.trace(
                        agent_id=agent_id,
                        input_data=input_data,
                        output_data={"error": str(e)},
                        status="error",
                        error_message=str(e),
                        metadata={"framework": "anthropic", "model": model},
                        duration_ms=duration_ms
                    )
                except:
                    pass
                raise
        
        anthropic.Anthropic.messages.create = traced_create
        self._is_patched = True
        logger.info("✅ Anthropic instrumentation enabled")
    
    def unpatch(self):
        if not self._is_patched:
            return
        try:
            import anthropic
            if 'messages_create' in self._original_methods:
                anthropic.Anthropic.messages.create = self._original_methods['messages_create']
        except ImportError:
            pass
        self._is_patched = False


# Global instrumentation registry
_instrumentations: Dict[str, InstrumentedFramework] = {}


def instrument_framework(
    client,
    framework: str = "auto",
    agent_prefix: str = ""
) -> List[str]:
    """
    Automatically instrument an AI framework for tracing.
    
    Args:
        client: AgentGuard client instance
        framework: Framework to instrument ("langchain", "openai", "anthropic", "crewai", "auto")
        agent_prefix: Prefix for auto-generated agent IDs
    
    Returns:
        List of frameworks that were instrumented
    
    Example:
        from agentguard import AgentGuard
        from agentguard.auto_instrument import instrument_framework
        
        ag = AgentGuard(api_key="ag_live_xxx")
        
        # Auto-detect and instrument all available frameworks
        instrumented = instrument_framework(ag, "auto")
        print(f"Instrumented: {instrumented}")
        
        # Or instrument specific framework
        instrument_framework(ag, "openai")
    """
    instrumented = []
    
    if framework == "auto":
        # Auto-detect installed frameworks
        detected = FrameworkDetector.detect_installed_frameworks()
        for fw in detected:
            result = instrument_framework(client, fw, agent_prefix)
            instrumented.extend(result)
        return instrumented
    
    framework = framework.lower()
    
    if framework in _instrumentations:
        logger.info(f"{framework} already instrumented")
        return [framework]
    
    if framework == "openai":
        inst = OpenAIInstrumentation(client, agent_prefix)
        inst.patch()
        _instrumentations[framework] = inst
        instrumented.append(framework)
    
    elif framework == "anthropic":
        inst = AnthropicInstrumentation(client, agent_prefix)
        inst.patch()
        _instrumentations[framework] = inst
        instrumented.append(framework)
    
    elif framework == "langchain":
        # LangChain uses callback handlers, no patching needed
        # Just return success - user should use AgentGuardCallbackHandler
        logger.info("LangChain: Use AgentGuardCallbackHandler for tracing")
        instrumented.append(framework)
    
    elif framework == "crewai":
        # CrewAI uses observers
        logger.info("CrewAI: Use AgentGuardObserver for tracing")
        instrumented.append(framework)
    
    else:
        logger.warning(f"Unknown framework: {framework}")
    
    return instrumented


def uninstrument_framework(framework: str = "all"):
    """Remove framework instrumentation."""
    if framework == "all":
        for fw, inst in _instrumentations.items():
            inst.unpatch()
        _instrumentations.clear()
    elif framework in _instrumentations:
        _instrumentations[framework].unpatch()
        del _instrumentations[framework]


def get_instrumented_frameworks() -> List[str]:
    """Get list of currently instrumented frameworks."""
    return list(_instrumentations.keys())


# Helper functions for serialization

def _serialize_args(args: tuple, kwargs: dict, func: Callable) -> Dict[str, Any]:
    """Safely serialize function arguments."""
    result = {}
    
    # Get argument names from function signature
    try:
        import inspect
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        
        for i, arg in enumerate(args):
            name = param_names[i] if i < len(param_names) else f"arg_{i}"
            result[name] = _safe_serialize(arg)
        
        for key, value in kwargs.items():
            result[key] = _safe_serialize(value)
    except:
        result["args"] = [_safe_serialize(a) for a in args]
        result["kwargs"] = {k: _safe_serialize(v) for k, v in kwargs.items()}
    
    return result


def _serialize_output(output: Any) -> Dict[str, Any]:
    """Safely serialize function output."""
    return {"result": _safe_serialize(output)}


def _safe_serialize(obj: Any, max_depth: int = 5, max_length: int = 10000) -> Any:
    """Safely serialize an object to JSON-compatible format."""
    if max_depth <= 0:
        return str(obj)[:100] + "..." if len(str(obj)) > 100 else str(obj)
    
    if obj is None:
        return None
    
    if isinstance(obj, (str, int, float, bool)):
        if isinstance(obj, str) and len(obj) > max_length:
            return obj[:max_length] + f"... (truncated, total {len(obj)} chars)"
        return obj
    
    if isinstance(obj, (list, tuple)):
        return [_safe_serialize(item, max_depth - 1, max_length) for item in obj[:100]]
    
    if isinstance(obj, dict):
        return {
            str(k): _safe_serialize(v, max_depth - 1, max_length) 
            for k, v in list(obj.items())[:100]
        }
    
    # Handle common AI response objects
    if hasattr(obj, 'model_dump'):  # Pydantic v2
        return _safe_serialize(obj.model_dump(), max_depth - 1, max_length)
    
    if hasattr(obj, 'dict'):  # Pydantic v1
        return _safe_serialize(obj.dict(), max_depth - 1, max_length)
    
    if hasattr(obj, '__dict__'):
        return _safe_serialize(
            {k: v for k, v in obj.__dict__.items() if not k.startswith('_')},
            max_depth - 1,
            max_length
        )
    
    # Fallback to string representation
    result = str(obj)
    if len(result) > max_length:
        return result[:max_length] + "..."
    return result


def _extract_tokens(response: Any) -> Optional[int]:
    """Try to extract token count from various response formats."""
    # OpenAI format
    if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
        return response.usage.total_tokens
    
    # Anthropic format
    if hasattr(response, 'usage'):
        usage = response.usage
        if hasattr(usage, 'input_tokens') and hasattr(usage, 'output_tokens'):
            return usage.input_tokens + usage.output_tokens
    
    # Dict format
    if isinstance(response, dict):
        if 'usage' in response:
            usage = response['usage']
            if isinstance(usage, dict):
                return usage.get('total_tokens') or \
                       (usage.get('input_tokens', 0) + usage.get('output_tokens', 0))
    
    return None


def _calculate_cost(response: Any, token_count: Optional[int]) -> Optional[float]:
    """Estimate cost based on response metadata."""
    if token_count is None:
        return None
    
    # Try to determine model for accurate pricing
    model = None
    if hasattr(response, 'model'):
        model = response.model
    elif isinstance(response, dict):
        model = response.get('model')
    
    # Rough pricing estimates (per 1K tokens)
    pricing = {
        'gpt-4': 0.06,
        'gpt-4-turbo': 0.03,
        'gpt-3.5-turbo': 0.002,
        'claude-3-opus': 0.075,
        'claude-3-sonnet': 0.015,
        'claude-3-haiku': 0.00125,
    }
    
    if model:
        for model_key, price in pricing.items():
            if model_key in model.lower():
                return (token_count / 1000) * price
    
    # Default estimate
    return (token_count / 1000) * 0.01


# Convenience exports
__all__ = [
    'auto_trace',
    'trace_block',
    'instrument_framework',
    'uninstrument_framework',
    'get_instrumented_frameworks',
    'FrameworkDetector',
    'TraceContext',
    'OpenAIInstrumentation',
    'AnthropicInstrumentation',
]

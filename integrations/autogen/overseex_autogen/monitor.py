"""
OverseeX AutoGen Monitor

Core monitoring functionality for Microsoft AutoGen multi-agent conversations.
Captures agent interactions, function calls, tool usage, and coordination patterns.
"""

from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime
from contextlib import contextmanager
import time
import logging
import json
import os
import requests
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("overseex.autogen")


class MessageType(str, Enum):
    """Types of messages in AutoGen conversations."""
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION_CALL = "function_call"
    FUNCTION_RESULT = "function_result"
    TERMINATION = "termination"


@dataclass
class AgentInfo:
    """Information about an AutoGen agent."""
    autogen_name: str
    overseex_id: Optional[str]
    agent_type: str  # AssistantAgent, UserProxyAgent, GroupChat, etc.
    system_message: Optional[str]
    llm_config: Optional[Dict]
    function_map: List[str]


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    sender: str
    receiver: str
    message_type: MessageType
    content: str
    function_name: Optional[str] = None
    function_args: Optional[Dict] = None
    function_result: Optional[Any] = None
    timestamp: float = field(default_factory=time.time)
    tokens_used: int = 0
    duration_ms: int = 0


@dataclass
class ConversationTrace:
    """Complete trace of a multi-agent conversation."""
    conversation_id: str
    agents: List[str]
    turns: List[ConversationTurn] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    status: str = "in_progress"
    total_tokens: int = 0
    total_function_calls: int = 0
    termination_reason: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class OverseeXAutoGenCallback:
    """
    Callback handler for AutoGen that captures conversation traces.

    This class hooks into AutoGen's message passing to capture:
    - Multi-turn conversations
    - Function/tool calls and results
    - Agent roles and behaviors
    - Coordination patterns between agents
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        capture_functions: bool = True,
        capture_messages: bool = True,
        capture_system_prompts: bool = False,
        auto_register_agents: bool = True,
        max_message_length: int = 2000,
        verbose: bool = False,
    ):
        """
        Initialize OverseeX callback for AutoGen.

        Args:
            api_key: OverseeX API key (ag_live_* or ag_test_*)
            base_url: OverseeX API URL (defaults to https://api.overseex.com)
            capture_functions: Whether to capture function calls
            capture_messages: Whether to capture message content
            capture_system_prompts: Whether to capture system prompts (may contain sensitive data)
            auto_register_agents: Whether to auto-register agents in OverseeX
            max_message_length: Maximum message length to capture
            verbose: Enable verbose logging
        """
        self.api_key = api_key
        self.base_url = base_url or os.getenv("OVERSEEX_API_URL", "https://api.overseex.com")
        self.capture_functions = capture_functions
        self.capture_messages = capture_messages
        self.capture_system_prompts = capture_system_prompts
        self.auto_register_agents = auto_register_agents
        self.max_message_length = max_message_length
        self.verbose = verbose

        # Internal state
        self.agents: Dict[str, AgentInfo] = {}
        self.active_conversations: Dict[str, ConversationTrace] = {}
        self.current_conversation_id: Optional[str] = None

        if verbose:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make API request to OverseeX."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code in (200, 201):
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    def _truncate(self, text: str, max_length: int = None) -> str:
        """Truncate text to max length."""
        max_length = max_length or self.max_message_length
        if not text or len(text) <= max_length:
            return text or ""
        return text[:max_length - 3] + "..."

    def register_agent(self, agent) -> Optional[str]:
        """
        Register an AutoGen agent with OverseeX.

        Args:
            agent: AutoGen Agent instance (AssistantAgent, UserProxyAgent, etc.)

        Returns:
            OverseeX agent ID if successful, None otherwise
        """
        agent_name = getattr(agent, 'name', str(id(agent)))

        if agent_name in self.agents:
            return self.agents[agent_name].overseex_id

        # Determine agent type
        agent_type = type(agent).__name__

        # Extract configuration
        system_message = None
        if self.capture_system_prompts:
            system_message = getattr(agent, 'system_message', None)

        llm_config = getattr(agent, 'llm_config', None)

        # Get function map
        function_map = []
        if hasattr(agent, 'function_map') and agent.function_map:
            function_map = list(agent.function_map.keys())

        agent_info = AgentInfo(
            autogen_name=agent_name,
            overseex_id=None,
            agent_type=agent_type,
            system_message=system_message,
            llm_config=llm_config,
            function_map=function_map,
        )

        if self.auto_register_agents:
            result = self._make_request("POST", "/api/v1/agents/", {
                "name": agent_name,
                "description": f"AutoGen {agent_type}",
                "endpoint_url": f"autogen://{agent_name}",
                "metadata": {
                    "agent_type": agent_type,
                    "functions": function_map,
                    "framework": "autogen",
                }
            })

            if result:
                agent_info.overseex_id = result.get("id")
                logger.info(f"Registered agent: {agent_name} -> {agent_info.overseex_id}")

        self.agents[agent_name] = agent_info
        return agent_info.overseex_id

    def start_conversation(self, agents: List, conversation_id: str = None) -> str:
        """
        Start tracking a new conversation.

        Args:
            agents: List of AutoGen agents participating
            conversation_id: Optional custom conversation ID

        Returns:
            Conversation ID
        """
        conv_id = conversation_id or f"conv_{int(time.time())}_{id(agents)}"

        # Register all agents
        agent_names = []
        for agent in agents:
            self.register_agent(agent)
            agent_names.append(getattr(agent, 'name', str(id(agent))))

        trace = ConversationTrace(
            conversation_id=conv_id,
            agents=agent_names,
            started_at=time.time(),
            metadata={
                "agent_count": len(agents),
                "agent_types": [type(a).__name__ for a in agents],
            }
        )

        self.active_conversations[conv_id] = trace
        self.current_conversation_id = conv_id

        logger.info(f"Started conversation: {conv_id} with {len(agents)} agents")
        return conv_id

    def on_message_sent(
        self,
        sender,
        receiver,
        message: Union[str, Dict],
        request_reply: bool = True,
    ):
        """
        Called when a message is sent from one agent to another.

        Args:
            sender: Sending agent
            receiver: Receiving agent
            message: Message content (string or dict with content/function_call)
            request_reply: Whether a reply was requested
        """
        if not self.current_conversation_id:
            return

        trace = self.active_conversations.get(self.current_conversation_id)
        if not trace:
            return

        sender_name = getattr(sender, 'name', str(id(sender)))
        receiver_name = getattr(receiver, 'name', str(id(receiver)))

        # Parse message
        if isinstance(message, dict):
            content = message.get('content', '')
            function_call = message.get('function_call')
        else:
            content = str(message)
            function_call = None

        # Determine message type
        if function_call:
            msg_type = MessageType.FUNCTION_CALL
            turn = ConversationTurn(
                sender=sender_name,
                receiver=receiver_name,
                message_type=msg_type,
                content=self._truncate(content) if self.capture_messages else "[REDACTED]",
                function_name=function_call.get('name'),
                function_args=function_call.get('arguments') if self.capture_functions else None,
            )
        else:
            msg_type = MessageType.ASSISTANT if hasattr(sender, 'llm_config') else MessageType.USER
            turn = ConversationTurn(
                sender=sender_name,
                receiver=receiver_name,
                message_type=msg_type,
                content=self._truncate(content) if self.capture_messages else "[REDACTED]",
            )

        trace.turns.append(turn)

        # Record handoff for coordination analysis
        self._record_handoff(sender_name, receiver_name, msg_type)

        logger.debug(f"Message: {sender_name} -> {receiver_name} ({msg_type.value})")

    def on_function_call(
        self,
        agent,
        function_name: str,
        arguments: Dict,
        result: Any,
        duration_ms: int = 0,
    ):
        """
        Called when an agent executes a function.

        Args:
            agent: Agent that called the function
            function_name: Name of the function
            arguments: Function arguments
            result: Function result
            duration_ms: Execution duration in milliseconds
        """
        if not self.capture_functions:
            return

        if not self.current_conversation_id:
            return

        trace = self.active_conversations.get(self.current_conversation_id)
        if not trace:
            return

        agent_name = getattr(agent, 'name', str(id(agent)))

        turn = ConversationTurn(
            sender=agent_name,
            receiver=agent_name,
            message_type=MessageType.FUNCTION_RESULT,
            content=f"Function: {function_name}",
            function_name=function_name,
            function_args=arguments,
            function_result=self._truncate(str(result), 1000),
            duration_ms=duration_ms,
        )

        trace.turns.append(turn)
        trace.total_function_calls += 1

        logger.debug(f"Function call: {agent_name} -> {function_name}")

    def on_llm_response(
        self,
        agent,
        response: Dict,
        tokens_used: int = 0,
    ):
        """
        Called when an LLM response is received.

        Args:
            agent: Agent that received the response
            response: LLM response
            tokens_used: Number of tokens used
        """
        if not self.current_conversation_id:
            return

        trace = self.active_conversations.get(self.current_conversation_id)
        if not trace:
            return

        trace.total_tokens += tokens_used

        # Update last turn with token info
        if trace.turns:
            trace.turns[-1].tokens_used = tokens_used

    def end_conversation(
        self,
        conversation_id: str = None,
        termination_reason: str = None,
        status: str = "completed",
    ):
        """
        End tracking a conversation and send trace to OverseeX.

        Args:
            conversation_id: Conversation ID (or use current)
            termination_reason: Why the conversation ended
            status: Final status (completed, error, timeout)
        """
        conv_id = conversation_id or self.current_conversation_id
        if not conv_id:
            return

        trace = self.active_conversations.get(conv_id)
        if not trace:
            return

        trace.completed_at = time.time()
        trace.status = status
        trace.termination_reason = termination_reason

        # Send trace to OverseeX
        self._send_conversation_trace(trace)

        # Cleanup
        del self.active_conversations[conv_id]
        if self.current_conversation_id == conv_id:
            self.current_conversation_id = None

        logger.info(f"Ended conversation: {conv_id} ({status})")

    def _record_handoff(self, from_agent: str, to_agent: str, message_type: MessageType):
        """Record agent handoff for coordination analysis."""
        from_info = self.agents.get(from_agent)
        to_info = self.agents.get(to_agent)

        if not from_info or not to_info:
            return

        if not from_info.overseex_id or not to_info.overseex_id:
            return

        # Send handoff to coordination API
        self._make_request("POST", "/api/v1/coordination/handoffs/", {
            "from_agent_id": from_info.overseex_id,
            "to_agent_id": to_info.overseex_id,
            "task_type": message_type.value,
            "status": "completed",
            "metadata": {
                "framework": "autogen",
                "conversation_id": self.current_conversation_id,
            }
        })

    def _send_conversation_trace(self, trace: ConversationTrace):
        """Send conversation trace to OverseeX."""
        # Find primary agent (first assistant agent)
        primary_agent_id = None
        for agent_name in trace.agents:
            agent_info = self.agents.get(agent_name)
            if agent_info and agent_info.overseex_id:
                if agent_info.agent_type == "AssistantAgent":
                    primary_agent_id = agent_info.overseex_id
                    break
                elif not primary_agent_id:
                    primary_agent_id = agent_info.overseex_id

        if not primary_agent_id:
            logger.warning("No registered agent found for trace")
            return

        # Build trace data
        duration_ms = int((trace.completed_at - trace.started_at) * 1000) if trace.completed_at else 0

        trace_data = {
            "agent_id": primary_agent_id,
            "input_data": {
                "conversation_id": trace.conversation_id,
                "agents": trace.agents,
                "first_message": trace.turns[0].content if trace.turns else None,
            },
            "output_data": {
                "total_turns": len(trace.turns),
                "total_tokens": trace.total_tokens,
                "total_function_calls": trace.total_function_calls,
                "last_message": trace.turns[-1].content if trace.turns else None,
                "termination_reason": trace.termination_reason,
            },
            "trace_data": {
                "llmCalls": [],
                "toolCalls": [
                    {
                        "tool": turn.function_name,
                        "input": str(turn.function_args)[:500] if turn.function_args else "",
                        "output": str(turn.function_result)[:500] if turn.function_result else "",
                        "durationMs": turn.duration_ms,
                        "timestamp": int(turn.timestamp * 1000),
                    }
                    for turn in trace.turns
                    if turn.message_type == MessageType.FUNCTION_RESULT
                ],
                "handoffs": [
                    {
                        "fromAgent": turn.sender,
                        "toAgent": turn.receiver,
                        "reason": turn.message_type.value,
                        "timestamp": int(turn.timestamp * 1000),
                    }
                    for turn in trace.turns
                    if turn.sender != turn.receiver
                ],
                "agentFlow": [
                    {
                        "agent": turn.sender,
                        "action": turn.message_type.value,
                        "timestamp": int(turn.timestamp * 1000),
                    }
                    for turn in trace.turns
                ],
            },
            "status": trace.status,
            "total_duration_ms": duration_ms,
            "metadata": {
                **trace.metadata,
                "framework": "autogen",
                "conversation_id": trace.conversation_id,
            },
            "tags": ["autogen", "multi-agent"],
        }

        result = self._make_request("POST", "/api/v1/traces/", trace_data)

        if result:
            logger.info(f"Trace sent: {result.get('id', 'unknown')}")
        else:
            logger.warning("Failed to send conversation trace")


class AutoGenMonitor:
    """
    Context manager for monitoring AutoGen conversations.

    Usage:
        with AutoGenMonitor(api_key="ag_live_...") as monitor:
            # Your AutoGen code here
            result = user_proxy.initiate_chat(assistant, message="Hello")
    """

    def __init__(self, api_key: str, **kwargs):
        """Initialize AutoGen monitor."""
        self.callback = OverseeXAutoGenCallback(api_key, **kwargs)
        self._original_methods = {}

    def __enter__(self):
        """Start monitoring."""
        self._install_hooks()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring."""
        self._uninstall_hooks()

        # End any active conversations
        for conv_id in list(self.callback.active_conversations.keys()):
            status = "error" if exc_type else "completed"
            self.callback.end_conversation(conv_id, status=status)

        return False

    def _install_hooks(self):
        """Install monitoring hooks into AutoGen."""
        try:
            from autogen import ConversableAgent

            # Store original methods
            self._original_methods['send'] = ConversableAgent.send
            self._original_methods['receive'] = ConversableAgent.receive

            callback = self.callback

            # Wrap send method
            original_send = ConversableAgent.send
            def monitored_send(self_agent, message, recipient, request_reply=None, silent=False):
                callback.on_message_sent(self_agent, recipient, message, request_reply)
                return original_send(self_agent, message, recipient, request_reply, silent)

            ConversableAgent.send = monitored_send

            logger.info("AutoGen hooks installed")

        except ImportError:
            logger.warning("AutoGen not installed, hooks not applied")

    def _uninstall_hooks(self):
        """Remove monitoring hooks from AutoGen."""
        try:
            from autogen import ConversableAgent

            if 'send' in self._original_methods:
                ConversableAgent.send = self._original_methods['send']
            if 'receive' in self._original_methods:
                ConversableAgent.receive = self._original_methods['receive']

            logger.info("AutoGen hooks removed")

        except ImportError:
            pass

    def start_chat(self, agents: List):
        """
        Manually start tracking a chat.

        Args:
            agents: List of agents in the conversation
        """
        return self.callback.start_conversation(agents)

    def end_chat(self, conversation_id: str = None, **kwargs):
        """
        Manually end tracking a chat.

        Args:
            conversation_id: Conversation to end
            **kwargs: Additional arguments for end_conversation
        """
        self.callback.end_conversation(conversation_id, **kwargs)


@contextmanager
def monitor_autogen(api_key: str, agents: List = None, **kwargs):
    """
    Context manager for monitoring AutoGen conversations.

    Args:
        api_key: OverseeX API key
        agents: Optional list of agents to register upfront
        **kwargs: Additional options for OverseeXAutoGenCallback

    Yields:
        OverseeXAutoGenCallback instance

    Usage:
        from autogen import AssistantAgent, UserProxyAgent

        assistant = AssistantAgent("assistant", llm_config=llm_config)
        user_proxy = UserProxyAgent("user_proxy")

        with monitor_autogen(api_key="ag_live_...", agents=[assistant, user_proxy]) as monitor:
            user_proxy.initiate_chat(assistant, message="What is the capital of France?")
    """
    callback = OverseeXAutoGenCallback(api_key, **kwargs)

    # Register agents if provided
    if agents:
        callback.start_conversation(agents)

    # Install hooks
    original_methods = {}
    try:
        from autogen import ConversableAgent

        original_methods['send'] = ConversableAgent.send

        original_send = ConversableAgent.send
        def monitored_send(self_agent, message, recipient, request_reply=None, silent=False):
            # Start conversation if not started
            if not callback.current_conversation_id:
                callback.start_conversation([self_agent, recipient])
            callback.on_message_sent(self_agent, recipient, message, request_reply)
            return original_send(self_agent, message, recipient, request_reply, silent)

        ConversableAgent.send = monitored_send

    except ImportError:
        logger.warning("AutoGen not installed")

    try:
        yield callback
    finally:
        # Restore original methods
        try:
            from autogen import ConversableAgent
            if 'send' in original_methods:
                ConversableAgent.send = original_methods['send']
        except ImportError:
            pass

        # End active conversations
        for conv_id in list(callback.active_conversations.keys()):
            callback.end_conversation(conv_id)

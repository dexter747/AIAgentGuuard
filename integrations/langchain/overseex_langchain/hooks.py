"""
OverseeX LangChain Hooks

Auto-instrumentation hooks for LangChain applications.
Automatically injects OverseeX callback handler into LangChain components.
"""

from typing import Optional, List, Any
import functools
import logging

logger = logging.getLogger("overseex.langchain.hooks")

# Store original methods for restoration
_original_methods = {}
_installed = False
_current_handler = None


def install_hooks(handler):
    """
    Install global hooks into LangChain.

    After calling this, all LangChain chain executions will be automatically traced.

    Args:
        handler: OverseeXCallbackHandler instance

    Example:
        from overseex_langchain import OverseeXCallbackHandler, install_hooks

        handler = OverseeXCallbackHandler(api_key="ox_live_xxx")
        install_hooks(handler)

        # All chains will now be traced automatically
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run("hello")  # Automatically traced!
    """
    global _installed, _current_handler, _original_methods

    if _installed:
        logger.warning("Hooks already installed")
        return

    _current_handler = handler

    try:
        # Try modern langchain_core first
        try:
            from langchain_core.runnables import RunnableSequence, RunnableParallel
            _hook_runnable(RunnableSequence, "invoke", handler)
            _hook_runnable(RunnableParallel, "invoke", handler)
            logger.info("Hooked langchain_core runnables")
        except ImportError:
            pass

        # Hook legacy chain
        try:
            from langchain.chains.base import Chain
            _hook_chain(Chain, handler)
            logger.info("Hooked langchain Chain")
        except ImportError:
            pass

        # Hook LLM
        try:
            from langchain.llms.base import BaseLLM
            _hook_llm(BaseLLM, handler)
            logger.info("Hooked langchain LLM")
        except ImportError:
            try:
                from langchain_core.language_models.llms import BaseLLM
                _hook_llm(BaseLLM, handler)
                logger.info("Hooked langchain_core LLM")
            except ImportError:
                pass

        # Hook ChatModel
        try:
            from langchain.chat_models.base import BaseChatModel
            _hook_chat_model(BaseChatModel, handler)
            logger.info("Hooked langchain ChatModel")
        except ImportError:
            try:
                from langchain_core.language_models.chat_models import BaseChatModel
                _hook_chat_model(BaseChatModel, handler)
                logger.info("Hooked langchain_core ChatModel")
            except ImportError:
                pass

        _installed = True
        logger.info("LangChain hooks installed successfully")

    except Exception as e:
        logger.error(f"Failed to install hooks: {e}")
        raise


def _hook_runnable(cls, method_name: str, handler):
    """Hook a Runnable method to inject callbacks."""
    original = getattr(cls, method_name)
    _original_methods[f"{cls.__name__}.{method_name}"] = original

    @functools.wraps(original)
    def wrapped(self, input, config=None, **kwargs):
        # Inject callback handler
        config = config or {}
        callbacks = config.get("callbacks", []) or []
        if handler not in callbacks:
            callbacks = list(callbacks) + [handler]
        config["callbacks"] = callbacks
        return original(self, input, config=config, **kwargs)

    setattr(cls, method_name, wrapped)


def _hook_chain(chain_cls, handler):
    """Hook Chain class to inject callbacks."""
    original_run = chain_cls.run
    original_call = chain_cls.__call__
    _original_methods["Chain.run"] = original_run
    _original_methods["Chain.__call__"] = original_call

    @functools.wraps(original_run)
    def wrapped_run(self, *args, callbacks=None, **kwargs):
        callbacks = callbacks or []
        if handler not in callbacks:
            callbacks = list(callbacks) + [handler]
        return original_run(self, *args, callbacks=callbacks, **kwargs)

    @functools.wraps(original_call)
    def wrapped_call(self, inputs, return_only_outputs=False, callbacks=None, **kwargs):
        callbacks = callbacks or []
        if handler not in callbacks:
            callbacks = list(callbacks) + [handler]
        return original_call(self, inputs, return_only_outputs=return_only_outputs, callbacks=callbacks, **kwargs)

    chain_cls.run = wrapped_run
    chain_cls.__call__ = wrapped_call


def _hook_llm(llm_cls, handler):
    """Hook LLM class to inject callbacks."""
    if hasattr(llm_cls, "generate"):
        original = llm_cls.generate
        _original_methods["BaseLLM.generate"] = original

        @functools.wraps(original)
        def wrapped(self, prompts, stop=None, callbacks=None, **kwargs):
            callbacks = callbacks or []
            if handler not in callbacks:
                callbacks = list(callbacks) + [handler]
            return original(self, prompts, stop=stop, callbacks=callbacks, **kwargs)

        llm_cls.generate = wrapped


def _hook_chat_model(chat_cls, handler):
    """Hook ChatModel class to inject callbacks."""
    if hasattr(chat_cls, "generate"):
        original = chat_cls.generate
        _original_methods["BaseChatModel.generate"] = original

        @functools.wraps(original)
        def wrapped(self, messages, stop=None, callbacks=None, **kwargs):
            callbacks = callbacks or []
            if handler not in callbacks:
                callbacks = list(callbacks) + [handler]
            return original(self, messages, stop=stop, callbacks=callbacks, **kwargs)

        chat_cls.generate = wrapped


def uninstall_hooks():
    """
    Remove installed hooks and restore original methods.
    """
    global _installed, _current_handler, _original_methods

    if not _installed:
        return

    # Restore RunnableSequence
    if "RunnableSequence.invoke" in _original_methods:
        try:
            from langchain_core.runnables import RunnableSequence
            RunnableSequence.invoke = _original_methods["RunnableSequence.invoke"]
        except ImportError:
            pass

    # Restore RunnableParallel
    if "RunnableParallel.invoke" in _original_methods:
        try:
            from langchain_core.runnables import RunnableParallel
            RunnableParallel.invoke = _original_methods["RunnableParallel.invoke"]
        except ImportError:
            pass

    # Restore Chain
    if "Chain.run" in _original_methods:
        try:
            from langchain.chains.base import Chain
            Chain.run = _original_methods["Chain.run"]
            Chain.__call__ = _original_methods["Chain.__call__"]
        except ImportError:
            pass

    # Restore LLM
    if "BaseLLM.generate" in _original_methods:
        try:
            from langchain.llms.base import BaseLLM
            BaseLLM.generate = _original_methods["BaseLLM.generate"]
        except ImportError:
            try:
                from langchain_core.language_models.llms import BaseLLM
                BaseLLM.generate = _original_methods["BaseLLM.generate"]
            except ImportError:
                pass

    # Restore ChatModel
    if "BaseChatModel.generate" in _original_methods:
        try:
            from langchain.chat_models.base import BaseChatModel
            BaseChatModel.generate = _original_methods["BaseChatModel.generate"]
        except ImportError:
            try:
                from langchain_core.language_models.chat_models import BaseChatModel
                BaseChatModel.generate = _original_methods["BaseChatModel.generate"]
            except ImportError:
                pass

    _original_methods.clear()
    _current_handler = None
    _installed = False

    logger.info("LangChain hooks uninstalled")


def get_current_handler():
    """Get the currently installed handler, if any."""
    return _current_handler


def is_hooks_installed() -> bool:
    """Check if hooks are currently installed."""
    return _installed

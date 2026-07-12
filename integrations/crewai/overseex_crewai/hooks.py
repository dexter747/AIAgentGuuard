"""
OverseeX CrewAI Hooks

Monkey-patching hooks for automatic CrewAI instrumentation.
This module modifies CrewAI classes to automatically capture traces
without requiring explicit callback registration.
"""

from typing import Optional
import functools
import logging

logger = logging.getLogger("overseex.crewai.hooks")

# Store original methods for restoration
_original_methods = {}
_installed = False
_current_callback = None


def install_hooks(callback):
    """
    Install global hooks into CrewAI.

    After calling this, all CrewAI Crew executions will be automatically traced.

    Args:
        callback: OverseeXCrewAICallback instance
    """
    global _installed, _current_callback, _original_methods

    if _installed:
        logger.warning("Hooks already installed")
        return

    _current_callback = callback

    try:
        from crewai import Crew
    except ImportError:
        logger.error("CrewAI is not installed")
        return

    # Store original methods
    _original_methods["kickoff"] = Crew.kickoff

    # Create wrapped method
    @functools.wraps(Crew.kickoff)
    def traced_kickoff(self, *args, **kwargs):
        """Wrapped kickoff method that captures traces."""
        try:
            _current_callback.on_crew_start(self)
        except Exception as e:
            logger.error(f"Error in on_crew_start: {e}")

        try:
            result = _original_methods["kickoff"](self, *args, **kwargs)

            try:
                _current_callback.on_crew_complete(self, result)
            except Exception as e:
                logger.error(f"Error in on_crew_complete: {e}")

            return result

        except Exception as e:
            logger.error(f"Crew execution failed: {e}")
            raise

    # Install hook
    Crew.kickoff = traced_kickoff
    _installed = True

    logger.info("CrewAI hooks installed")


def uninstall_hooks():
    """
    Remove installed hooks and restore original methods.
    """
    global _installed, _current_callback, _original_methods

    if not _installed:
        return

    try:
        from crewai import Crew
    except ImportError:
        return

    # Restore original methods
    if "kickoff" in _original_methods:
        Crew.kickoff = _original_methods["kickoff"]

    _original_methods.clear()
    _current_callback = None
    _installed = False

    logger.info("CrewAI hooks uninstalled")


def install_crew_hooks(crew, callback):
    """
    Install hooks for a specific Crew instance.

    This is less invasive than global hooks - it only affects the specific crew.

    Args:
        crew: CrewAI Crew instance
        callback: OverseeXCrewAICallback instance
    """
    original_kickoff = crew.kickoff

    @functools.wraps(original_kickoff)
    def traced_kickoff(*args, **kwargs):
        try:
            # Track task execution
            _hook_task_execution(crew, callback)
        except Exception as e:
            logger.error(f"Error setting up task hooks: {e}")

        try:
            result = original_kickoff(*args, **kwargs)

            try:
                callback.on_crew_complete(crew, result)
            except Exception as e:
                logger.error(f"Error in on_crew_complete: {e}")

            return result

        except Exception as e:
            logger.error(f"Crew execution failed: {e}")
            raise

    # Bind the wrapped method to the crew instance
    import types
    crew.kickoff = types.MethodType(lambda self, *args, **kwargs: traced_kickoff(*args, **kwargs), crew)


def _hook_task_execution(crew, callback):
    """
    Hook into task execution for the crew.

    This attempts to intercept task execution to capture per-task traces.
    """
    # Try to hook into _execute_task if it exists
    if hasattr(crew, '_execute_task'):
        original_execute = crew._execute_task

        @functools.wraps(original_execute)
        def traced_execute(task, agent, *args, **kwargs):
            try:
                callback.on_task_start(task, agent, crew)
            except Exception as e:
                logger.error(f"Error in on_task_start: {e}")

            try:
                result = original_execute(task, agent, *args, **kwargs)

                try:
                    callback.on_task_complete(task, agent, result, crew)
                except Exception as e:
                    logger.error(f"Error in on_task_complete: {e}")

                return result

            except Exception as e:
                try:
                    callback.on_task_error(task, agent, e, crew)
                except Exception as err:
                    logger.error(f"Error in on_task_error: {err}")
                raise

        import types
        crew._execute_task = types.MethodType(
            lambda self, task, agent, *args, **kwargs: traced_execute(task, agent, *args, **kwargs),
            crew
        )

    # Also try to hook into agent tool execution
    for agent in crew.agents:
        _hook_agent_tools(agent, callback)


def _hook_agent_tools(agent, callback):
    """
    Hook into agent tool execution.

    Args:
        agent: CrewAI Agent instance
        callback: OverseeXCrewAICallback instance
    """
    if not hasattr(agent, 'tools') or not agent.tools:
        return

    for tool in agent.tools:
        if hasattr(tool, '_run'):
            original_run = tool._run

            @functools.wraps(original_run)
            def traced_tool_run(tool_input, *args, tool=tool, **kwargs):
                try:
                    result = original_run(tool_input, *args, **kwargs)

                    try:
                        callback.on_tool_call(agent, tool.__class__.__name__, tool_input, result)
                    except Exception as e:
                        logger.error(f"Error in on_tool_call: {e}")

                    return result
                except Exception as e:
                    try:
                        callback.on_tool_call(agent, tool.__class__.__name__, tool_input, f"ERROR: {e}")
                    except Exception as err:
                        logger.error(f"Error in on_tool_call: {err}")
                    raise

            tool._run = traced_tool_run


def get_current_callback():
    """Get the currently installed callback, if any."""
    return _current_callback


def is_hooks_installed() -> bool:
    """Check if hooks are currently installed."""
    return _installed

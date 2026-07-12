"""
OverseeX LangChain Tracer

Advanced tracer for hierarchical trace capture with full run tree support.
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime
import time
import logging
import requests

logger = logging.getLogger("overseex.langchain.tracer")

try:
    from langchain.callbacks.tracers.base import BaseTracer
    from langchain.callbacks.tracers.schemas import Run
except ImportError:
    try:
        from langchain_core.tracers.base import BaseTracer
        from langchain_core.tracers.schemas import Run
    except ImportError:
        BaseTracer = None
        Run = None


if BaseTracer is not None:
    class OverseeXTracer(BaseTracer):
        """
        LangChain tracer that captures hierarchical execution traces.

        This tracer provides more detailed traces than the callback handler,
        including full run tree structure with parent-child relationships.

        Usage:
            from overseex_langchain import OverseeXTracer

            tracer = OverseeXTracer(api_key="ox_live_xxx")

            chain = LLMChain(llm=llm, prompt=prompt)
            result = chain.run("hello", callbacks=[tracer])
        """

        def __init__(
            self,
            api_key: str,
            agent_id: Optional[str] = None,
            base_url: str = "https://api.overseex.com",
            project_name: str = "default",
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
        ):
            """
            Initialize OverseeX tracer.

            Args:
                api_key: OverseeX API key
                agent_id: Agent ID for traces
                base_url: OverseeX API base URL
                project_name: Project name for organization
                tags: Tags for traces
                metadata: Additional metadata
            """
            super().__init__(**kwargs)
            self.api_key = api_key
            self.base_url = base_url.rstrip("/")
            self.agent_id = agent_id or "langchain-default"
            self.project_name = project_name
            self.tags = tags or []
            self.extra_metadata = metadata or {}

            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            })

            # Track runs for hierarchical tracing
            self._runs: Dict[UUID, Run] = {}

        def _persist_run(self, run: Run) -> None:
            """Persist a run to OverseeX."""
            # Only send top-level runs
            if run.parent_run_id is not None:
                return

            # Build the trace from the run tree
            trace_data = self._build_trace_data(run)

            try:
                response = self._session.post(
                    f"{self.base_url}/api/v1/traces",
                    json=trace_data,
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Trace persisted: {data.get('id')}")
                else:
                    logger.warning(f"Failed to persist trace: {response.text}")
            except Exception as e:
                logger.error(f"Error persisting trace: {e}")

        def _build_trace_data(self, run: Run) -> Dict[str, Any]:
            """Build trace data from a run tree."""
            # Calculate duration
            duration_ms = 0
            if run.end_time and run.start_time:
                duration_ms = int((run.end_time - run.start_time).total_seconds() * 1000)

            # Extract LLM calls, tool calls, etc. from child runs
            llm_calls = []
            tool_calls = []
            retrieval_queries = []
            total_tokens = 0

            def process_run(r: Run):
                nonlocal total_tokens

                if r.run_type == "llm":
                    tokens = r.extra.get("tokens", 0) if r.extra else 0
                    total_tokens += tokens
                    llm_calls.append({
                        "model": r.name,
                        "inputs": r.inputs,
                        "outputs": r.outputs,
                        "token_count": tokens,
                        "duration_ms": int((r.end_time - r.start_time).total_seconds() * 1000) if r.end_time and r.start_time else 0,
                    })
                elif r.run_type == "tool":
                    tool_calls.append({
                        "tool": r.name,
                        "input": str(r.inputs)[:500] if r.inputs else "",
                        "output": str(r.outputs)[:500] if r.outputs else "",
                        "duration_ms": int((r.end_time - r.start_time).total_seconds() * 1000) if r.end_time and r.start_time else 0,
                    })
                elif r.run_type == "retriever":
                    retrieval_queries.append({
                        "query": str(r.inputs)[:500] if r.inputs else "",
                        "results": r.outputs,
                        "duration_ms": int((r.end_time - r.start_time).total_seconds() * 1000) if r.end_time and r.start_time else 0,
                    })

                # Process child runs
                for child in r.child_runs or []:
                    process_run(child)

            process_run(run)

            return {
                "agent_id": self.agent_id,
                "input_data": run.inputs or {},
                "output_data": run.outputs or {},
                "status": "success" if run.error is None else "error",
                "error_message": run.error,
                "total_duration_ms": duration_ms,
                "token_count": total_tokens,
                "trace_data": {
                    "run_type": run.run_type,
                    "run_name": run.name,
                    "llm_calls": llm_calls,
                    "tool_calls": tool_calls,
                    "retrieval_queries": retrieval_queries,
                    "run_tree": self._serialize_run_tree(run),
                },
                "metadata": {
                    **self.extra_metadata,
                    "framework": "langchain",
                    "project": self.project_name,
                },
                "tags": self.tags,
            }

        def _serialize_run_tree(self, run: Run, depth: int = 0) -> Dict[str, Any]:
            """Serialize a run tree for visualization."""
            if depth > 10:  # Prevent infinite recursion
                return {"name": run.name, "truncated": True}

            return {
                "id": str(run.id),
                "name": run.name,
                "type": run.run_type,
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "end_time": run.end_time.isoformat() if run.end_time else None,
                "error": run.error,
                "children": [
                    self._serialize_run_tree(child, depth + 1)
                    for child in (run.child_runs or [])
                ],
            }

        def _on_llm_start(self, run: Run) -> None:
            """Process LLM start event."""
            self._runs[run.id] = run

        def _on_llm_end(self, run: Run) -> None:
            """Process LLM end event."""
            self._runs[run.id] = run

        def _on_llm_error(self, run: Run) -> None:
            """Process LLM error event."""
            self._runs[run.id] = run

        def _on_chain_start(self, run: Run) -> None:
            """Process chain start event."""
            self._runs[run.id] = run

        def _on_chain_end(self, run: Run) -> None:
            """Process chain end event."""
            self._runs[run.id] = run
            self._persist_run(run)

        def _on_chain_error(self, run: Run) -> None:
            """Process chain error event."""
            self._runs[run.id] = run
            self._persist_run(run)

        def _on_tool_start(self, run: Run) -> None:
            """Process tool start event."""
            self._runs[run.id] = run

        def _on_tool_end(self, run: Run) -> None:
            """Process tool end event."""
            self._runs[run.id] = run

        def _on_tool_error(self, run: Run) -> None:
            """Process tool error event."""
            self._runs[run.id] = run

        def _on_retriever_start(self, run: Run) -> None:
            """Process retriever start event."""
            self._runs[run.id] = run

        def _on_retriever_end(self, run: Run) -> None:
            """Process retriever end event."""
            self._runs[run.id] = run

        def _on_retriever_error(self, run: Run) -> None:
            """Process retriever error event."""
            self._runs[run.id] = run

        def close(self):
            """Close the tracer and clean up resources."""
            self._session.close()

else:
    class OverseeXTracer:
        """Placeholder tracer when LangChain is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "LangChain tracer requires langchain-core. "
                "Install with: pip install langchain-core"
            )

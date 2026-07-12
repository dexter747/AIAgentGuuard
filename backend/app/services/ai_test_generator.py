"""
AI-Powered Test Generation Service

Uses LLM to intelligently generate high-quality test cases from execution traces.
Falls back to template-based generation when LLM is unavailable.
"""
import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)


class AITestGenerator:
    """
    Intelligent test generation using LLM for understanding and generating tests.
    
    Features:
    - Semantic understanding of agent behavior
    - Edge case identification
    - Assertion generation based on expected behavior
    - Mock generation for external APIs
    - Test coverage analysis
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview",
        fallback_to_template: bool = True
    ):
        """
        Initialize AI Test Generator.
        
        Args:
            openai_api_key: OpenAI API key (or from env OPENAI_API_KEY)
            anthropic_api_key: Anthropic API key (or from env ANTHROPIC_API_KEY)
            model: Model to use for generation
            fallback_to_template: Use template-based generation if LLM fails
        """
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.fallback_to_template = fallback_to_template
        self._openai_client = None
        self._anthropic_client = None
        
        # Initialize clients
        self._init_clients()
    
    def _init_clients(self):
        """Initialize LLM clients."""
        if self.openai_api_key:
            try:
                import openai
                self._openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized for test generation")
            except ImportError:
                logger.warning("OpenAI package not installed")
        
        if self.anthropic_api_key:
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                logger.info("Anthropic client initialized for test generation")
            except ImportError:
                logger.warning("Anthropic package not installed")
    
    @property
    def llm_available(self) -> bool:
        """Check if any LLM client is available."""
        return self._openai_client is not None or self._anthropic_client is not None
    
    def generate_test_from_trace(
        self,
        trace: Dict[str, Any],
        agent_name: str,
        context: Optional[str] = None,
        test_framework: str = "pytest"
    ) -> Dict[str, Any]:
        """
        Generate a test case from a single execution trace.
        
        Args:
            trace: Trace data containing input, output, status, etc.
            agent_name: Name of the agent being tested
            context: Additional context about the agent's purpose
            test_framework: Test framework to use (pytest, unittest)
        
        Returns:
            Dict with:
                - code: Generated test code
                - test_name: Name of the test
                - description: What the test validates
                - assertions: List of assertions in the test
                - mocks: List of mocks needed
                - llm_generated: Whether LLM was used
        """
        if self.llm_available:
            try:
                return self._generate_with_llm(trace, agent_name, context, test_framework)
            except Exception as e:
                logger.warning(f"LLM generation failed: {e}, falling back to template")
                if self.fallback_to_template:
                    return self._generate_with_template(trace, agent_name, test_framework)
                raise
        else:
            return self._generate_with_template(trace, agent_name, test_framework)
    
    def _generate_with_llm(
        self,
        trace: Dict[str, Any],
        agent_name: str,
        context: Optional[str],
        test_framework: str
    ) -> Dict[str, Any]:
        """Generate test using LLM."""
        
        # Build prompt for test generation
        prompt = self._build_test_generation_prompt(trace, agent_name, context, test_framework)
        
        # Call LLM
        if self._openai_client:
            response = self._call_openai(prompt)
        elif self._anthropic_client:
            response = self._call_anthropic(prompt)
        else:
            raise RuntimeError("No LLM client available")
        
        # Parse response
        return self._parse_test_response(response, trace)
    
    def _build_test_generation_prompt(
        self,
        trace: Dict[str, Any],
        agent_name: str,
        context: Optional[str],
        test_framework: str
    ) -> str:
        """Build prompt for LLM test generation."""
        
        input_data = trace.get("input_data", trace.get("input", {}))
        output_data = trace.get("output_data", trace.get("output", {}))
        status = trace.get("status", "success")
        error = trace.get("error_message", "")
        metadata = trace.get("metadata", {})
        tool_calls = metadata.get("tool_calls", [])
        duration_ms = trace.get("duration_ms", 0)
        
        prompt = f"""You are an expert test engineer. Generate a comprehensive {test_framework} test for the following AI agent execution trace.

## Agent Information
- Name: {agent_name}
- Context: {context or "AI agent for processing user requests"}

## Execution Trace
- Status: {status}
- Duration: {duration_ms}ms
- Error: {error or "None"}

### Input:
```json
{json.dumps(input_data, indent=2, default=str)[:2000]}
```

### Output:
```json
{json.dumps(output_data, indent=2, default=str)[:2000]}
```

### Tool Calls Made:
```json
{json.dumps(tool_calls[:10], indent=2, default=str) if tool_calls else "None"}
```

## Requirements

Generate a {test_framework} test that:
1. Tests the exact behavior observed in this trace
2. Includes appropriate mocks for any external API calls
3. Has meaningful assertions (not just "assert True")
4. Includes edge case handling if the trace suggests any
5. Has clear docstrings explaining what's being tested
6. Uses realistic test data based on the input

## Response Format

Respond with a JSON object containing:
```json
{{
    "test_name": "test_descriptive_name",
    "description": "What this test validates",
    "code": "full pytest code here",
    "assertions": ["list of what's being asserted"],
    "mocks_needed": ["list of APIs/services that need mocking"],
    "edge_cases": ["potential edge cases identified"]
}}
```

Generate ONLY the JSON response, no other text."""
        
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self._openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert test engineer who writes high-quality, comprehensive tests."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        response = self._anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _parse_test_response(self, response: str, trace: Dict) -> Dict[str, Any]:
        """Parse LLM response into structured test data."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                data['llm_generated'] = True
                return data
        except json.JSONDecodeError:
            pass
        
        # Fallback: extract code block if JSON parsing fails
        code_match = re.search(r'```python\n([\s\S]*?)\n```', response)
        code = code_match.group(1) if code_match else response
        
        return {
            "test_name": f"test_trace_{trace.get('id', 'unknown')[:8]}",
            "description": "Auto-generated test from trace",
            "code": code,
            "assertions": [],
            "mocks_needed": [],
            "llm_generated": True
        }
    
    def _generate_with_template(
        self,
        trace: Dict[str, Any],
        agent_name: str,
        test_framework: str
    ) -> Dict[str, Any]:
        """Generate test using template-based approach."""
        
        input_data = trace.get("input_data", trace.get("input", {}))
        output_data = trace.get("output_data", trace.get("output", {}))
        status = trace.get("status", "success")
        metadata = trace.get("metadata", {})
        tool_calls = metadata.get("tool_calls", [])
        duration_ms = trace.get("duration_ms", 0)
        
        # Generate test name
        test_name = self._generate_test_name(input_data, status)
        
        # Build assertions
        assertions = self._generate_assertions(input_data, output_data, status, tool_calls)
        
        # Build mocks
        mocks = self._generate_mocks(tool_calls)
        
        # Generate code
        code = self._build_template_code(
            test_name=test_name,
            agent_name=agent_name,
            input_data=input_data,
            output_data=output_data,
            status=status,
            assertions=assertions,
            mocks=mocks,
            duration_ms=duration_ms
        )
        
        return {
            "test_name": test_name,
            "description": f"Test for {status} case with input pattern",
            "code": code,
            "assertions": [a['description'] for a in assertions],
            "mocks_needed": list(mocks.keys()),
            "llm_generated": False
        }
    
    def _generate_test_name(self, input_data: Any, status: str) -> str:
        """Generate descriptive test name."""
        prefix = "test_" if status == "success" else "test_error_"
        
        if isinstance(input_data, dict):
            # Use first key or message type
            keys = list(input_data.keys())[:2]
            suffix = "_".join(keys) if keys else "case"
        elif isinstance(input_data, str):
            # Use first few words
            words = re.sub(r'[^a-zA-Z0-9\s]', '', input_data[:50]).split()[:3]
            suffix = "_".join(words) if words else "case"
        else:
            suffix = "case"
        
        return f"{prefix}{suffix.lower()}"
    
    def _generate_assertions(
        self,
        input_data: Any,
        output_data: Any,
        status: str,
        tool_calls: List
    ) -> List[Dict[str, Any]]:
        """Generate assertions based on trace data."""
        assertions = []
        
        # Basic status assertion
        if status == "success":
            assertions.append({
                "type": "not_none",
                "description": "Result should not be None",
                "code": "assert result is not None"
            })
            assertions.append({
                "type": "no_error",
                "description": "Result should not contain error",
                "code": "assert 'error' not in str(result).lower()"
            })
        else:
            assertions.append({
                "type": "error_handling",
                "description": "Error should be handled gracefully",
                "code": "# Error case - verify graceful handling"
            })
        
        # Output type assertion
        if output_data:
            output_type = type(output_data).__name__
            assertions.append({
                "type": "output_type",
                "description": f"Output should be {output_type}",
                "code": f"assert isinstance(result, {output_type})"
            })
        
        # Output content assertions
        if isinstance(output_data, dict) and status == "success":
            for key in list(output_data.keys())[:3]:
                assertions.append({
                    "type": "output_key",
                    "description": f"Output should contain '{key}'",
                    "code": f"assert '{key}' in result or hasattr(result, '{key}')"
                })
        
        # Tool call assertions
        for tool in tool_calls[:5]:
            tool_name = tool.get("name", tool.get("tool", "unknown"))
            assertions.append({
                "type": "tool_called",
                "description": f"Tool '{tool_name}' should be called",
                "code": f"assert mocks['{tool_name}'].called"
            })
        
        return assertions
    
    def _generate_mocks(self, tool_calls: List) -> Dict[str, Dict]:
        """Generate mock configurations from tool calls."""
        mocks = {}
        
        for tool in tool_calls:
            tool_name = tool.get("name", tool.get("tool", "unknown"))
            tool_input = tool.get("input", tool.get("args", {}))
            tool_output = tool.get("output", tool.get("response", {}))
            
            mocks[tool_name] = {
                "input_pattern": tool_input,
                "response": tool_output,
                "call_count": 1
            }
        
        return mocks
    
    def _build_template_code(
        self,
        test_name: str,
        agent_name: str,
        input_data: Any,
        output_data: Any,
        status: str,
        assertions: List[Dict],
        mocks: Dict[str, Dict],
        duration_ms: int
    ) -> str:
        """Build test code from template."""
        
        code = f'''import pytest
from unittest.mock import MagicMock, patch
from agentguard import mock_tools


@pytest.mark.agentguard
def {test_name}():
    """
    Auto-generated test for {agent_name}
    Status: {status}
    Generated: {datetime.utcnow().isoformat()}
    
    This test validates the agent behavior observed in production traces.
    """
    # Input data from trace
    input_data = {json.dumps(input_data, indent=8, default=str)}
    
'''
        
        # Add mock setup
        if mocks:
            code += "    # Set up mocks for external dependencies\n"
            code += "    with mock_tools() as mocks:\n"
            for mock_name, mock_config in mocks.items():
                response = json.dumps(mock_config['response'], default=str)
                code += f"        mocks['{mock_name}'].return_value = {response}\n"
            code += "\n"
            indent = "        "
        else:
            indent = "    "
        
        # Add agent execution
        code += f"{indent}# Execute agent\n"
        code += f"{indent}# TODO: Initialize your agent here\n"
        code += f"{indent}# agent = {agent_name}()\n"
        code += f"{indent}# result = agent.run(input_data)\n"
        code += f"{indent}result = None  # Replace with actual execution\n\n"
        
        # Add assertions
        code += f"{indent}# Assertions\n"
        for assertion in assertions:
            code += f"{indent}{assertion['code']}  # {assertion['description']}\n"
        
        # Add performance check
        if duration_ms > 0:
            max_duration = max(duration_ms * 2, 5000)
            code += f"\n{indent}# Performance check (trace: {duration_ms}ms)\n"
            code += f"{indent}# assert execution_time < {max_duration}\n"
        
        return code
    
    def generate_test_suite(
        self,
        traces: List[Dict[str, Any]],
        agent_name: str,
        context: Optional[str] = None,
        max_tests: int = 20
    ) -> Dict[str, Any]:
        """
        Generate a complete test suite from multiple traces.
        
        Args:
            traces: List of trace data
            agent_name: Name of the agent
            context: Additional context
            max_tests: Maximum number of tests to generate
        
        Returns:
            Dict with:
                - code: Complete test suite code
                - test_count: Number of tests generated
                - coverage: Estimated coverage info
                - summary: Summary of test suite
        """
        # Categorize traces
        success_traces = [t for t in traces if t.get("status") == "success"]
        error_traces = [t for t in traces if t.get("status") in ["error", "failed"]]
        
        # Select diverse traces
        selected_traces = self._select_diverse_traces(
            success_traces[:max_tests // 2] + error_traces[:max_tests // 4],
            max_count=max_tests
        )
        
        # Generate individual tests
        tests = []
        for trace in selected_traces:
            try:
                test = self.generate_test_from_trace(trace, agent_name, context)
                tests.append(test)
            except Exception as e:
                logger.warning(f"Failed to generate test: {e}")
        
        # Combine into suite
        suite_code = self._build_test_suite(tests, agent_name)
        
        # Analyze coverage
        coverage = self._analyze_coverage(traces, tests)
        
        return {
            "code": suite_code,
            "test_count": len(tests),
            "tests": tests,
            "coverage": coverage,
            "summary": f"Generated {len(tests)} tests covering {coverage['scenarios']} scenarios"
        }
    
    def _select_diverse_traces(
        self,
        traces: List[Dict],
        max_count: int
    ) -> List[Dict]:
        """Select diverse traces to maximize coverage."""
        if len(traces) <= max_count:
            return traces
        
        selected = []
        seen_patterns = set()
        
        for trace in traces:
            # Create pattern hash from input structure
            input_data = trace.get("input_data", trace.get("input", {}))
            pattern = self._get_input_pattern(input_data)
            
            if pattern not in seen_patterns:
                selected.append(trace)
                seen_patterns.add(pattern)
                
                if len(selected) >= max_count:
                    break
        
        return selected
    
    def _get_input_pattern(self, input_data: Any) -> str:
        """Get pattern hash for input data."""
        if isinstance(input_data, dict):
            keys = sorted(input_data.keys())
            return hashlib.md5(str(keys).encode()).hexdigest()[:8]
        elif isinstance(input_data, str):
            # Pattern based on first words
            words = input_data.split()[:5]
            return hashlib.md5(" ".join(words).encode()).hexdigest()[:8]
        return "default"
    
    def _build_test_suite(self, tests: List[Dict], agent_name: str) -> str:
        """Combine individual tests into a test suite."""
        
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', agent_name)
        
        code = f'''"""
Auto-generated Test Suite for {agent_name}
Generated by OverseeX AI Test Generator
Date: {datetime.utcnow().isoformat()}

This test suite was generated from production traces to ensure
the agent behavior remains consistent.
"""

import pytest
from unittest.mock import MagicMock, patch
from agentguard import mock_tools


class Test{safe_name}Suite:
    """Test suite for {agent_name}"""
    
    @pytest.fixture
    def agent(self):
        """Initialize the agent for testing."""
        # TODO: Initialize your {agent_name} agent here
        # return {safe_name}()
        return MagicMock()
    
'''
        
        # Add each test as a method
        for i, test in enumerate(tests):
            test_code = test.get("code", "")
            # Convert to class method
            method_code = self._convert_to_class_method(
                test_code,
                test.get("test_name", f"test_case_{i}")
            )
            code += method_code + "\n"
        
        return code
    
    def _convert_to_class_method(self, test_code: str, test_name: str) -> str:
        """Convert standalone test to class method."""
        # Extract just the function body
        lines = test_code.split('\n')
        
        # Find where the function body starts
        body_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                body_start = i + 1
                break
        
        # Get body lines
        body_lines = lines[body_start:]
        
        # Build method
        method = f"    def {test_name}(self, agent):\n"
        for line in body_lines:
            if line.strip():
                method += f"    {line}\n"
            else:
                method += "\n"
        
        return method
    
    def _analyze_coverage(
        self,
        all_traces: List[Dict],
        generated_tests: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze test coverage."""
        
        total_traces = len(all_traces)
        tested_patterns = len(generated_tests)
        
        # Count unique input patterns
        input_patterns = set()
        for trace in all_traces:
            pattern = self._get_input_pattern(trace.get("input_data", trace.get("input", {})))
            input_patterns.add(pattern)
        
        # Count statuses
        statuses = {}
        for trace in all_traces:
            status = trace.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total_traces": total_traces,
            "unique_patterns": len(input_patterns),
            "tests_generated": tested_patterns,
            "scenarios": tested_patterns,
            "status_distribution": statuses,
            "pattern_coverage": f"{(tested_patterns / max(len(input_patterns), 1)) * 100:.1f}%"
        }
    
    def identify_edge_cases(
        self,
        traces: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze traces to identify potential edge cases for testing.
        
        Returns list of identified edge cases with recommendations.
        """
        edge_cases = []
        
        for trace in traces:
            input_data = str(trace.get("input_data", trace.get("input", "")))
            output_data = trace.get("output_data", trace.get("output", {}))
            status = trace.get("status", "success")
            duration_ms = trace.get("duration_ms", 0)
            metadata = trace.get("metadata", {})
            
            reasons = []
            
            # Empty or minimal input
            if len(input_data.strip()) < 10:
                reasons.append("Empty or minimal input")
            
            # Very long input
            if len(input_data) > 5000:
                reasons.append("Very long input (potential truncation)")
            
            # Special characters
            if re.search(r'[<>{}|\\^~\[\]`\x00-\x1f]', input_data):
                reasons.append("Special characters in input")
            
            # Unicode edge cases
            if any(ord(c) > 127 for c in input_data):
                reasons.append("Non-ASCII characters")
            
            # Slow execution
            if duration_ms > 30000:
                reasons.append(f"Slow execution ({duration_ms}ms)")
            
            # Very fast execution (might be cached/skipped)
            if duration_ms < 10 and status == "success":
                reasons.append("Suspiciously fast execution")
            
            # High token usage
            tokens = trace.get("token_count", metadata.get("tokens_used", 0))
            if tokens > 4000:
                reasons.append(f"High token usage ({tokens})")
            
            # Error case
            if status in ["error", "failed"]:
                error = trace.get("error_message", "")
                reasons.append(f"Error case: {error[:100]}")
            
            if reasons:
                edge_cases.append({
                    "trace_id": trace.get("id"),
                    "reasons": reasons,
                    "input_preview": input_data[:200],
                    "status": status,
                    "recommendation": self._get_edge_case_recommendation(reasons)
                })
        
        return edge_cases
    
    def _get_edge_case_recommendation(self, reasons: List[str]) -> str:
        """Get recommendation for handling edge case."""
        recommendations = []
        
        for reason in reasons:
            if "empty" in reason.lower():
                recommendations.append("Add input validation and meaningful error message")
            elif "long" in reason.lower():
                recommendations.append("Implement input truncation or chunking")
            elif "special" in reason.lower() or "unicode" in reason.lower():
                recommendations.append("Sanitize input and test with various encodings")
            elif "slow" in reason.lower():
                recommendations.append("Add timeout handling and performance monitoring")
            elif "error" in reason.lower():
                recommendations.append("Ensure graceful error handling and user feedback")
        
        return "; ".join(recommendations) if recommendations else "Review and add appropriate handling"


# Singleton instance
ai_test_generator = AITestGenerator()

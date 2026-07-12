"""
Basic Tracing Example

Shows how to use OverseeX for basic function tracing.
"""

import os
import asyncio
from overseex import OverseeX

# Initialize the client
client = OverseeX(
    api_key=os.environ.get("OVERSEEX_API_KEY", "ox_test_xxx"),
    debug=True,
)


# Example 1: Decorator-based tracing
@client.trace
def simple_function(query: str) -> str:
    """A simple function that gets automatically traced."""
    return f"Processed: {query}"


# Example 2: Decorator with options
@client.trace(name="custom_processor", tags=["production"])
def process_with_options(data: dict) -> dict:
    """Function with custom trace options."""
    return {"result": data.get("value", 0) * 2}


# Example 3: Manual span with context manager
def complex_operation():
    """More control with manual spans."""
    with client.span("complex_operation", tags=["manual"]) as span:
        span.set_input({"task": "analyze data"})

        # Record an LLM call
        span.record_llm_call(
            model="gpt-4",
            messages=[{"role": "user", "content": "Analyze this data"}],
            response={"role": "assistant", "content": "Analysis complete"},
            usage={"tokens": 150, "latency_ms": 500},
        )

        # Record a tool call
        span.record_tool_call(
            tool_name="data_lookup",
            input_data={"id": "123"},
            output_data={"name": "Test", "value": 42},
        )

        span.set_output({"success": True, "insights": ["insight1", "insight2"]})
        span.set_status("success")

    return "Operation complete"


def main():
    # Run simple traced function
    result1 = simple_function("What is the weather today?")
    print(f"Simple function result: {result1}")

    # Run with custom options
    result2 = process_with_options({"value": 21})
    print(f"Custom processor result: {result2}")

    # Run complex operation
    result3 = complex_operation()
    print(f"Complex operation result: {result3}")

    print("\nTracing complete!")


if __name__ == "__main__":
    main()

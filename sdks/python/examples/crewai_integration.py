"""
CrewAI Integration Example

Shows how to use OverseeX with CrewAI for multi-agent workflow monitoring.
Requires: pip install crewai overseex-crewai
"""

import os

# Check if crewai is installed
try:
    from crewai import Agent, Task, Crew, Process
    from overseex_crewai import instrument_crewai, OverseeXCrewAICallback
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("CrewAI not installed. Run: pip install crewai overseex-crewai")


def example_with_auto_instrumentation():
    """
    Example 1: Zero-code instrumentation

    Simply call instrument_crewai() to automatically trace all CrewAI operations.
    """
    # Auto-instrument all CrewAI classes
    instrument_crewai(
        api_key=os.environ.get("OVERSEEX_API_KEY", "ox_test_xxx"),
        capture_thoughts=True,
        capture_tool_results=True,
    )

    # Create agents as normal
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Research and analyze AI trends",
        backstory="You are an expert at finding and analyzing information.",
        verbose=True,
    )

    writer = Agent(
        role="Content Writer",
        goal="Create compelling content from research",
        backstory="You excel at transforming research into engaging content.",
        verbose=True,
    )

    # Create tasks
    research_task = Task(
        description="Research the latest developments in AI agents",
        expected_output="A comprehensive summary of AI agent trends",
        agent=researcher,
    )

    writing_task = Task(
        description="Write a blog post based on the research",
        expected_output="A well-written blog post about AI agents",
        agent=writer,
    )

    # Create and run crew - all operations are automatically traced
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return result


def example_with_callback():
    """
    Example 2: Callback-based instrumentation

    Use the callback for more control over what gets captured.
    """
    # Create callback
    callback = OverseeXCrewAICallback(
        api_key=os.environ.get("OVERSEEX_API_KEY", "ox_test_xxx"),
        capture_agent_thoughts=True,
        capture_task_results=True,
    )

    # Create agents
    analyst = Agent(
        role="Data Analyst",
        goal="Analyze data patterns",
        backstory="You are skilled at finding patterns in data.",
        verbose=True,
    )

    # Create task
    analysis_task = Task(
        description="Analyze the provided dataset for trends",
        expected_output="A report on data trends",
        agent=analyst,
    )

    # Create crew with callback
    crew = Crew(
        agents=[analyst],
        tasks=[analysis_task],
        callbacks=[callback],  # Add the OverseeX callback
        verbose=True,
    )

    result = crew.kickoff()
    return result


def main():
    if not CREWAI_AVAILABLE:
        print("\nThis example requires CrewAI to be installed.")
        print("Install it with: pip install crewai overseex-crewai")
        return

    print("=== CrewAI + OverseeX Integration Example ===\n")

    # Run auto-instrumentation example
    print("Running auto-instrumented crew...")
    result = example_with_auto_instrumentation()
    print(f"Result: {result}\n")

    # Run callback example
    print("Running callback-instrumented crew...")
    result = example_with_callback()
    print(f"Result: {result}\n")

    print("Check your OverseeX dashboard to see the traces!")


if __name__ == "__main__":
    main()

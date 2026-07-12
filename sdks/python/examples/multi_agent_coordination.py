"""
Multi-Agent Coordination Example

Shows how to use OverseeX coordination intelligence features
for monitoring multi-agent systems.
"""

import os
from overseex import OverseeX


def main():
    client = OverseeX(
        api_key=os.environ.get("OVERSEEX_API_KEY", "ox_test_xxx"),
    )

    # Example 1: Record agent handoffs in a multi-agent workflow
    with client.span("orchestrator_agent", tags=["multi-agent", "orchestrator"]) as span:
        span.set_input({"task": "Research and summarize AI news"})

        # Delegate to research agent
        span.record_handoff(
            from_agent="orchestrator-001",
            to_agent="researcher-001",
            context={"task": "Find recent AI news articles"},
            handoff_type="delegation",
        )

        # Simulate research agent work (in real code, this would be async)
        import time
        time.sleep(0.1)

        # Research agent hands back to orchestrator
        span.record_handoff(
            from_agent="researcher-001",
            to_agent="orchestrator-001",
            context={"articles": ["article1", "article2", "article3"]},
            handoff_type="completion",
        )

        # Delegate to summarizer agent
        span.record_handoff(
            from_agent="orchestrator-001",
            to_agent="summarizer-001",
            context={
                "articles": ["article1", "article2", "article3"],
                "format": "bullet_points",
            },
            handoff_type="delegation",
        )

        time.sleep(0.05)

        # Summarizer completes
        span.record_handoff(
            from_agent="summarizer-001",
            to_agent="orchestrator-001",
            context={"summary": "• AI advancement 1\n• AI advancement 2"},
            handoff_type="completion",
        )

        span.set_output({"summary": "• AI advancement 1\n• AI advancement 2"})
        span.set_status("success")

    # Example 2: Check for coordination issues
    print("\n--- Checking Coordination Issues ---")
    issues = client.coordination.list_issues(
        severity="high",
        status="open",
        limit=10,
    )

    if issues:
        print(f"Found {len(issues)} open high-severity issues:")
        for issue in issues:
            print(f"  - [{issue.issue_type}] {issue.description}")
    else:
        print("No high-severity issues found!")

    # Example 3: Get corrective suggestions
    print("\n--- Checking Suggestions ---")
    suggestions = client.coordination.list_suggestions(
        min_confidence=0.7,
        status="pending",
    )

    if suggestions:
        print(f"Found {len(suggestions)} suggestions:")
        for suggestion in suggestions:
            print(
                f"  - [{suggestion.confidence * 100:.0f}%] {suggestion.suggestion_text}"
            )

            # Example: Approve a suggestion
            # client.coordination.approve_suggestion(
            #     suggestion.id,
            #     feedback_notes="Implemented successfully"
            # )
    else:
        print("No pending suggestions found!")

    # Example 4: View learned patterns
    print("\n--- Learned Patterns ---")
    patterns = client.coordination.list_patterns(is_active=True, limit=5)

    if patterns:
        print(f"{len(patterns)} active patterns:")
        for pattern in patterns:
            print(
                f"  - [{pattern.issue_type}] {pattern.pattern_name} "
                f"({pattern.success_rate * 100:.0f}% success)"
            )
    else:
        print("No patterns learned yet.")

    # Example 5: Get coordination metrics
    print("\n--- Coordination Metrics ---")
    metrics = client.coordination.get_metrics(days=7)
    print("Last 7 days:")
    print(f"  Total issues: {metrics.total_issues}")
    print(f"  Issues by type: {metrics.issues_by_type}")
    print(f"  Total handoffs: {metrics.total_handoffs}")
    print(f"  Handoff success rate: {metrics.handoff_success_rate * 100:.1f}%")

    # Example 6: Analyze specific traces for issues
    print("\n--- Analyzing Traces ---")
    # Uncomment to analyze traces:
    # analysis = client.coordination.analyze_traces(
    #     trace_ids=["trace-1", "trace-2"],
    #     auto_create_issues=True,
    # )
    # print(f"Analysis result: {analysis}")

    print("\nCoordination example complete!")


if __name__ == "__main__":
    main()

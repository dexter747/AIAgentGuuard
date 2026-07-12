/**
 * Multi-Agent Coordination Example
 *
 * Shows how to use OverseeX coordination intelligence features
 * for monitoring multi-agent systems.
 */

import { OverseeX } from '../src';

async function main() {
  const client = new OverseeX({
    apiKey: process.env.OVERSEEX_API_KEY || 'ox_test_xxx',
  });

  // Example 1: Record agent handoffs
  const orchestratorAgent = client.createSpan('orchestrator_agent', {
    tags: ['multi-agent', 'orchestrator'],
  });

  try {
    orchestratorAgent.setInput({ task: 'Research and summarize AI news' });

    // Delegate to research agent
    orchestratorAgent.recordHandoff(
      'orchestrator-001',
      'researcher-001',
      { task: 'Find recent AI news articles' },
      'delegation'
    );

    // Simulate research agent work
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Research agent hands back to orchestrator
    orchestratorAgent.recordHandoff(
      'researcher-001',
      'orchestrator-001',
      { articles: ['article1', 'article2', 'article3'] },
      'completion'
    );

    // Delegate to summarizer agent
    orchestratorAgent.recordHandoff(
      'orchestrator-001',
      'summarizer-001',
      { articles: ['article1', 'article2', 'article3'], format: 'bullet_points' },
      'delegation'
    );

    // Simulate summarizer work
    await new Promise((resolve) => setTimeout(resolve, 50));

    // Summarizer completes
    orchestratorAgent.recordHandoff(
      'summarizer-001',
      'orchestrator-001',
      { summary: '• AI advancement 1\n• AI advancement 2\n• AI advancement 3' },
      'completion'
    );

    orchestratorAgent.setOutput({
      summary: '• AI advancement 1\n• AI advancement 2\n• AI advancement 3',
    });
    orchestratorAgent.setStatus('success');
  } finally {
    await orchestratorAgent.end(client);
  }

  // Example 2: Check for coordination issues
  console.log('\n--- Checking Coordination Issues ---');
  const issues = await client.coordination.listIssues({
    severity: 'high',
    status: 'open',
    limit: 10,
  });

  if (issues.length > 0) {
    console.log(`Found ${issues.length} open high-severity issues:`);
    for (const issue of issues) {
      console.log(`  - [${issue.issue_type}] ${issue.description}`);
    }
  } else {
    console.log('No high-severity issues found!');
  }

  // Example 3: Get corrective suggestions
  console.log('\n--- Checking Suggestions ---');
  const suggestions = await client.coordination.listSuggestions({
    minConfidence: 0.7,
    status: 'pending',
  });

  if (suggestions.length > 0) {
    console.log(`Found ${suggestions.length} suggestions:`);
    for (const suggestion of suggestions) {
      console.log(
        `  - [${(suggestion.confidence * 100).toFixed(0)}%] ${suggestion.suggestion_text}`
      );

      // Example: Approve a suggestion
      // await client.coordination.approveSuggestion(
      //   suggestion.id,
      //   'Implemented successfully'
      // );
    }
  } else {
    console.log('No pending suggestions found!');
  }

  // Example 4: View learned patterns
  console.log('\n--- Learned Patterns ---');
  const patterns = await client.coordination.listPatterns({
    isActive: true,
    limit: 5,
  });

  if (patterns.length > 0) {
    console.log(`${patterns.length} active patterns:`);
    for (const pattern of patterns) {
      console.log(
        `  - [${pattern.issue_type}] ${pattern.pattern_name} (${pattern.success_rate * 100}% success)`
      );
    }
  } else {
    console.log('No patterns learned yet.');
  }

  // Example 5: Get coordination metrics
  console.log('\n--- Coordination Metrics ---');
  const metrics = await client.coordination.getMetrics({ days: 7 });
  console.log('Last 7 days:');
  console.log(`  Total issues: ${metrics.total_issues}`);
  console.log(`  Issues by type:`, metrics.issues_by_type);
  console.log(`  Total handoffs: ${metrics.total_handoffs}`);
  console.log(`  Handoff success rate: ${(metrics.handoff_success_rate * 100).toFixed(1)}%`);
}

main().catch(console.error);

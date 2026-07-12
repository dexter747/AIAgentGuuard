/**
 * OverseeX LangChain.js Integration
 *
 * Callback handler for automatic tracing of LangChain chains and agents.
 *
 * @example
 * ```typescript
 * import { ChatOpenAI } from '@langchain/openai';
 * import { OverseeXCallbackHandler } from '@overseex/langchain';
 *
 * const handler = new OverseeXCallbackHandler({
 *   apiKey: 'your-overseex-api-key',
 *   agentId: 'your-agent-id'
 * });
 *
 * const llm = new ChatOpenAI({
 *   callbacks: [handler]
 * });
 * ```
 */

import type {
  BaseCallbackHandler,
  CallbackHandlerMethods,
} from '@langchain/core/callbacks/base';
import type { Serialized } from '@langchain/core/load/serializable';
import type { LLMResult } from '@langchain/core/outputs';
import type { ChainValues } from '@langchain/core/utils/types';
import type { AgentAction, AgentFinish } from '@langchain/core/agents';
import type { Document } from '@langchain/core/documents';

export interface OverseeXConfig {
  apiKey: string;
  agentId?: string;
  baseUrl?: string;
  capturePrompts?: boolean;
  captureResponses?: boolean;
  captureToolCalls?: boolean;
  debug?: boolean;
}

interface RunState {
  runId: string;
  parentRunId?: string;
  startTime: number;
  type: 'llm' | 'chain' | 'tool' | 'agent';
  name: string;
  inputs?: any;
  outputs?: any;
  error?: string;
  tokens?: { prompt: number; completion: number; total: number };
  children: string[];
}

/**
 * OverseeX callback handler for LangChain.js
 *
 * Captures all LLM calls, chain executions, tool usage, and agent actions.
 */
export class OverseeXCallbackHandler implements Partial<CallbackHandlerMethods> {
  name = 'OverseeXCallbackHandler';
  private config: Required<OverseeXConfig>;
  private baseUrl: string;
  private runs: Map<string, RunState> = new Map();
  private rootRunId?: string;

  constructor(config: OverseeXConfig) {
    this.config = {
      apiKey: config.apiKey,
      agentId: config.agentId || 'langchain-agent',
      baseUrl: config.baseUrl || 'https://api.overseex.com',
      capturePrompts: config.capturePrompts ?? true,
      captureResponses: config.captureResponses ?? true,
      captureToolCalls: config.captureToolCalls ?? true,
      debug: config.debug ?? false,
    };
    this.baseUrl = this.config.baseUrl.replace(/\/$/, '');
  }

  private log(...args: any[]) {
    if (this.config.debug) {
      console.log('[OverseeX]', ...args);
    }
  }

  private truncate(text: string, maxLength: number = 1000): string {
    if (!text || text.length <= maxLength) return text || '';
    return text.slice(0, maxLength - 3) + '...';
  }

  private async sendTrace(rootRun: RunState): Promise<void> {
    const llmCalls: any[] = [];
    const toolCalls: any[] = [];
    const handoffs: any[] = [];

    // Collect all runs
    const collectRuns = (runId: string) => {
      const run = this.runs.get(runId);
      if (!run) return;

      if (run.type === 'llm') {
        llmCalls.push({
          model: run.name,
          prompt: this.config.capturePrompts ? this.truncate(JSON.stringify(run.inputs)) : '[REDACTED]',
          response: this.config.captureResponses ? this.truncate(JSON.stringify(run.outputs)) : '[REDACTED]',
          tokens: run.tokens?.total || 0,
          durationMs: Date.now() - run.startTime,
          timestamp: run.startTime,
        });
      } else if (run.type === 'tool') {
        toolCalls.push({
          tool: run.name,
          input: this.config.captureToolCalls ? this.truncate(JSON.stringify(run.inputs)) : '[REDACTED]',
          output: this.config.captureToolCalls ? this.truncate(JSON.stringify(run.outputs)) : '[REDACTED]',
          durationMs: Date.now() - run.startTime,
          timestamp: run.startTime,
        });
      }

      run.children.forEach(collectRuns);
    };

    collectRuns(rootRun.runId);

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/traces`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: this.config.agentId,
          input_data: this.config.capturePrompts ? rootRun.inputs : { redacted: true },
          output_data: this.config.captureResponses ? rootRun.outputs : { redacted: true },
          trace_data: {
            llmCalls,
            toolCalls,
            handoffs,
            agentFlow: [],
          },
          status: rootRun.error ? 'error' : 'success',
          error_message: rootRun.error,
          total_duration_ms: Date.now() - rootRun.startTime,
          metadata: {
            framework: 'langchain-js',
            chainName: rootRun.name,
            llmCallCount: llmCalls.length,
            toolCallCount: toolCalls.length,
          },
          tags: ['langchain', 'javascript'],
        }),
      });

      if (!response.ok) {
        this.log('Failed to send trace:', response.status);
      } else {
        this.log('Trace sent successfully');
      }
    } catch (error) {
      this.log('Error sending trace:', error);
    }
  }

  // LLM Callbacks
  async handleLLMStart(
    llm: Serialized,
    prompts: string[],
    runId: string,
    parentRunId?: string,
    extraParams?: Record<string, unknown>,
    tags?: string[],
    metadata?: Record<string, unknown>
  ): Promise<void> {
    this.log('LLM Start:', llm.id?.join('/') || 'unknown', runId);

    const run: RunState = {
      runId,
      parentRunId,
      startTime: Date.now(),
      type: 'llm',
      name: llm.id?.join('/') || 'unknown-llm',
      inputs: prompts,
      children: [],
    };

    this.runs.set(runId, run);

    if (parentRunId) {
      const parent = this.runs.get(parentRunId);
      if (parent) parent.children.push(runId);
    }
  }

  async handleLLMEnd(output: LLMResult, runId: string): Promise<void> {
    this.log('LLM End:', runId);

    const run = this.runs.get(runId);
    if (run) {
      run.outputs = output.generations;
      if (output.llmOutput?.tokenUsage) {
        run.tokens = {
          prompt: output.llmOutput.tokenUsage.promptTokens || 0,
          completion: output.llmOutput.tokenUsage.completionTokens || 0,
          total: output.llmOutput.tokenUsage.totalTokens || 0,
        };
      }
    }
  }

  async handleLLMError(err: Error, runId: string): Promise<void> {
    this.log('LLM Error:', runId, err.message);

    const run = this.runs.get(runId);
    if (run) {
      run.error = err.message;
    }
  }

  // Chain Callbacks
  async handleChainStart(
    chain: Serialized,
    inputs: ChainValues,
    runId: string,
    parentRunId?: string
  ): Promise<void> {
    this.log('Chain Start:', chain.id?.join('/') || 'unknown', runId);

    const run: RunState = {
      runId,
      parentRunId,
      startTime: Date.now(),
      type: 'chain',
      name: chain.id?.join('/') || 'unknown-chain',
      inputs,
      children: [],
    };

    this.runs.set(runId, run);

    // Track root run
    if (!parentRunId) {
      this.rootRunId = runId;
    } else {
      const parent = this.runs.get(parentRunId);
      if (parent) parent.children.push(runId);
    }
  }

  async handleChainEnd(outputs: ChainValues, runId: string): Promise<void> {
    this.log('Chain End:', runId);

    const run = this.runs.get(runId);
    if (run) {
      run.outputs = outputs;

      // If this is the root run, send the trace
      if (runId === this.rootRunId) {
        await this.sendTrace(run);
        this.cleanup();
      }
    }
  }

  async handleChainError(err: Error, runId: string): Promise<void> {
    this.log('Chain Error:', runId, err.message);

    const run = this.runs.get(runId);
    if (run) {
      run.error = err.message;

      // If this is the root run, send the trace
      if (runId === this.rootRunId) {
        await this.sendTrace(run);
        this.cleanup();
      }
    }
  }

  // Tool Callbacks
  async handleToolStart(
    tool: Serialized,
    input: string,
    runId: string,
    parentRunId?: string
  ): Promise<void> {
    this.log('Tool Start:', tool.id?.join('/') || 'unknown', runId);

    const run: RunState = {
      runId,
      parentRunId,
      startTime: Date.now(),
      type: 'tool',
      name: tool.id?.join('/') || 'unknown-tool',
      inputs: input,
      children: [],
    };

    this.runs.set(runId, run);

    if (parentRunId) {
      const parent = this.runs.get(parentRunId);
      if (parent) parent.children.push(runId);
    }
  }

  async handleToolEnd(output: string, runId: string): Promise<void> {
    this.log('Tool End:', runId);

    const run = this.runs.get(runId);
    if (run) {
      run.outputs = output;
    }
  }

  async handleToolError(err: Error, runId: string): Promise<void> {
    this.log('Tool Error:', runId, err.message);

    const run = this.runs.get(runId);
    if (run) {
      run.error = err.message;
    }
  }

  // Agent Callbacks
  async handleAgentAction(action: AgentAction, runId: string): Promise<void> {
    this.log('Agent Action:', action.tool, runId);
  }

  async handleAgentEnd(action: AgentFinish, runId: string): Promise<void> {
    this.log('Agent End:', runId);
  }

  // Retriever Callbacks
  async handleRetrieverStart(
    retriever: Serialized,
    query: string,
    runId: string,
    parentRunId?: string
  ): Promise<void> {
    this.log('Retriever Start:', retriever.id?.join('/') || 'unknown', runId);
  }

  async handleRetrieverEnd(
    documents: Document[],
    runId: string
  ): Promise<void> {
    this.log('Retriever End:', runId, `${documents.length} documents`);
  }

  private cleanup(): void {
    this.runs.clear();
    this.rootRunId = undefined;
  }
}

/**
 * Create an OverseeX callback handler for LangChain.js
 */
export function createOverseeXHandler(config: OverseeXConfig): OverseeXCallbackHandler {
  return new OverseeXCallbackHandler(config);
}

export default OverseeXCallbackHandler;

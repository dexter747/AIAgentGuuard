/**
 * OverseeX TypeScript/JavaScript SDK
 *
 * The complete testing & monitoring platform for AI agents.
 *
 * @example
 * ```typescript
 * import { OverseeX } from '@overseex/sdk';
 *
 * const client = new OverseeX({ apiKey: 'ox_live_xxx' });
 *
 * // Wrap your agent
 * const tracedAgent = client.wrap(myAgent);
 * const result = await tracedAgent.run('Hello');
 *
 * // Access coordination features
 * const issues = await client.coordination.listIssues();
 * ```
 */

export { OverseeX } from './client';
export { CoordinationClient } from './coordination';
export { Span, createSpan } from './tracing';
export * from './types';

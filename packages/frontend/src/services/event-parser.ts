import type { AgentEvent } from '../types/contracts.js';

/**
 * Parse the `data` field of a Server-Sent Event into a typed AgentEvent.
 *
 * Throws if the payload is not valid JSON.
 */
export function parseAgentEvent(data: string): AgentEvent {
  const parsed: AgentEvent = JSON.parse(data);

  // Minimal runtime guard — make sure essential fields exist
  if (!parsed.eventType || !parsed.conversationId) {
    throw new Error(
      `Invalid AgentEvent: missing eventType or conversationId — ${data}`,
    );
  }

  return parsed;
}

import type { AgentEvent, UserResponse } from '../types/contracts.js';
import { parseAgentEvent } from './event-parser.js';

/**
 * Lightweight HTTP + SSE client for the agent backend.
 */
export class AgentAPIClient {
  private readonly baseUrl: string;
  private readonly token: string;

  constructor(baseUrl: string, token: string = '') {
    // Strip trailing slash for consistency
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.token = token;
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /** Create a new conversation and return its id. */
  async createConversation(agentId: string): Promise<{ id: string }> {
    const res = await fetch(`${this.baseUrl}/conversations`, {
      method: 'POST',
      headers: this._headers(),
      body: JSON.stringify({ agentId }),
    });
    if (!res.ok) {
      throw new Error(`Failed to create conversation: ${res.status} ${res.statusText}`);
    }
    return res.json() as Promise<{ id: string }>;
  }

  /** Send a user response (text, form submit, choice, etc.) to a conversation. */
  async sendMessage(conversationId: string, message: UserResponse): Promise<void> {
    const res = await fetch(
      `${this.baseUrl}/conversations/${conversationId}/messages`,
      {
        method: 'POST',
        headers: this._headers(),
        body: JSON.stringify(message),
      },
    );
    if (!res.ok) {
      throw new Error(`Failed to send message: ${res.status} ${res.statusText}`);
    }
  }

  /**
   * Open an SSE stream for agent events on the given conversation.
   *
   * Returns the underlying EventSource so the caller can close it when done.
   */
  streamEvents(
    conversationId: string,
    onEvent: (event: AgentEvent) => void,
    onError?: (err: Event) => void,
  ): EventSource {
    const url = `${this.baseUrl}/conversations/${conversationId}/events`;
    const es = new EventSource(url);

    es.onmessage = (msg: MessageEvent<string>) => {
      try {
        const parsed = parseAgentEvent(msg.data);
        onEvent(parsed);
      } catch {
        console.error('[AgentAPIClient] Failed to parse SSE event', msg.data);
      }
    };

    es.onerror = (err) => {
      if (onError) {
        onError(err);
      } else {
        console.error('[AgentAPIClient] SSE error', err);
      }
    };

    return es;
  }

  // -------------------------------------------------------------------------
  // Private helpers
  // -------------------------------------------------------------------------

  private _headers(): Record<string, string> {
    const h: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };
    if (this.token) {
      h['Authorization'] = `Bearer ${this.token}`;
    }
    return h;
  }
}

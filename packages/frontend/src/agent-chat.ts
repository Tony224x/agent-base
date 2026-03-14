import { LitElement, html, css, nothing } from 'lit';
import { customElement, property, state, query } from 'lit/decorators.js';

// Types
import type {
  AgentEvent,
  UIComponent,
  UserResponse,
} from './types/contracts.js';

// Services
import { AgentAPIClient } from './services/api-client.js';

// Components — importing them registers the custom elements
import './components/chat-message.js';
import './components/chat-form.js';
import './components/chat-choice-list.js';
import './components/chat-confirmation.js';
import './components/chat-card-list.js';

// Registry — register built-in components
import { registerComponent } from './components/component-registry.js';
import { ChatMessage } from './components/chat-message.js';
import { ChatForm } from './components/chat-form.js';
import { ChatChoiceList } from './components/chat-choice-list.js';
import { ChatConfirmation } from './components/chat-confirmation.js';
import { ChatCardList } from './components/chat-card-list.js';

registerComponent('message', ChatMessage as never);
registerComponent('form', ChatForm as never);
registerComponent('choice-list', ChatChoiceList as never);
registerComponent('confirmation', ChatConfirmation as never);
registerComponent('card-list', ChatCardList as never);

// Re-export public API
export { registerComponent, getComponent, hasComponent } from './components/component-registry.js';
export { AgentAPIClient } from './services/api-client.js';
export type * from './types/contracts.js';

// ---------------------------------------------------------------------------
// Internal types used only inside this component
// ---------------------------------------------------------------------------

interface ChatEntry {
  id: string;
  role: 'user' | 'agent';
  component?: UIComponent;
  text?: string;
  /** Accumulates streamed tokens before they get finalised into a message */
  streaming?: boolean;
}

// ---------------------------------------------------------------------------
// <agent-chat> — main Web Component
// ---------------------------------------------------------------------------

@customElement('agent-chat')
export class AgentChat extends LitElement {
  // -----------------------------------------------------------------------
  // Styles
  // -----------------------------------------------------------------------
  static override styles = css`
    /* ---- tokens (importable via CSS custom properties) ---- */
    :host {
      --_primary: var(--agent-primary-color, #0071e3);
      --_bg: var(--agent-bg-color, #ffffff);
      --_surface: var(--agent-surface-color, #f5f5f7);
      --_text: var(--agent-text-color, #1d1d1f);
      --_border: var(--agent-border-color, #e5e5ea);
      --_radius: var(--agent-border-radius, 12px);
      --_font: var(--agent-font-family, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
      --_error: var(--agent-error-color, #ff3b30);
      --_success: var(--agent-success-color, #34c759);

      display: flex;
      flex-direction: column;
      height: 100%;
      font-family: var(--_font);
      background: var(--_bg);
      color: var(--_text);
      overflow: hidden;
    }

    /* Dark theme */
    :host([theme="dark"]) {
      --_bg: #1c1c1e;
      --_surface: #2c2c2e;
      --_text: #f5f5f7;
      --_border: #38383a;
    }

    /* Auto theme follows OS preference */
    @media (prefers-color-scheme: dark) {
      :host([theme="auto"]) {
        --_bg: #1c1c1e;
        --_surface: #2c2c2e;
        --_text: #f5f5f7;
        --_border: #38383a;
      }
    }

    /* ---- Header ---- */
    .header {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.875rem 1.25rem;
      border-bottom: 1px solid var(--_border);
      background: var(--_bg);
      flex-shrink: 0;
    }
    .header-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--_success);
      flex-shrink: 0;
    }
    .header-dot.offline {
      background: var(--_border);
    }
    .header-dot.connecting {
      background: #ff9f0a;
      animation: pulse 1.2s ease-in-out infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.35; }
    }
    .header-title {
      font-size: 0.875rem;
      font-weight: 600;
      flex: 1;
    }
    .header-status {
      font-size: 0.6875rem;
      color: var(--_text);
      opacity: 0.5;
    }

    /* ---- Messages area ---- */
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      scroll-behavior: smooth;
    }
    .messages::-webkit-scrollbar {
      width: 6px;
    }
    .messages::-webkit-scrollbar-track {
      background: transparent;
    }
    .messages::-webkit-scrollbar-thumb {
      background: var(--_border);
      border-radius: 3px;
    }

    /* ---- Bubble wrappers ---- */
    .bubble-row {
      display: flex;
      animation: fadeSlideIn 0.25s ease-out both;
    }
    @keyframes fadeSlideIn {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .bubble-row.agent {
      justify-content: flex-start;
    }
    .bubble-row.user {
      justify-content: flex-end;
    }

    .bubble {
      max-width: 85%;
      padding: 0.75rem 1rem;
      border-radius: var(--_radius);
      line-height: 1.5;
      font-size: 0.9375rem;
    }
    .bubble.agent {
      background: var(--_surface);
      border-bottom-left-radius: 4px;
    }
    .bubble.user {
      background: var(--_primary);
      color: #fff;
      border-bottom-right-radius: 4px;
    }

    /* Component bubbles (forms, cards, etc.) get slightly different treatment */
    .bubble.agent.component-bubble {
      background: transparent;
      padding: 0;
      max-width: 92%;
    }

    /* ---- Thinking / tool indicator ---- */
    .thinking {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 0;
      font-size: 0.75rem;
      color: var(--_text);
      opacity: 0.55;
      animation: fadeSlideIn 0.25s ease-out both;
    }
    .thinking-dots {
      display: flex;
      gap: 3px;
    }
    .thinking-dots span {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: currentColor;
      animation: dotBounce 1.4s ease-in-out infinite;
    }
    .thinking-dots span:nth-child(2) { animation-delay: 0.16s; }
    .thinking-dots span:nth-child(3) { animation-delay: 0.32s; }
    @keyframes dotBounce {
      0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
      40% { transform: scale(1); opacity: 1; }
    }

    /* ---- Input area ---- */
    .input-area {
      display: flex;
      align-items: flex-end;
      gap: 0.5rem;
      padding: 0.75rem 1rem;
      border-top: 1px solid var(--_border);
      background: var(--_bg);
      flex-shrink: 0;
    }

    .input-field {
      flex: 1;
      min-height: 40px;
      max-height: 120px;
      padding: 0.5rem 0.875rem;
      font-family: inherit;
      font-size: 0.875rem;
      color: var(--_text);
      background: var(--_surface);
      border: 1px solid var(--_border);
      border-radius: 20px;
      outline: none;
      resize: none;
      line-height: 1.45;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .input-field:focus {
      border-color: var(--_primary);
      box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
    }
    .input-field::placeholder {
      color: var(--_text);
      opacity: 0.4;
    }

    .send-btn {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border: none;
      background: var(--_primary);
      color: #fff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: filter 0.15s ease, transform 0.1s ease;
    }
    .send-btn:hover {
      filter: brightness(1.1);
    }
    .send-btn:active {
      transform: scale(0.92);
    }
    .send-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    .send-btn svg {
      width: 18px;
      height: 18px;
    }

    /* ---- Empty / welcome state ---- */
    .empty-state {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 2rem;
      gap: 0.75rem;
      opacity: 0.5;
    }
    .empty-state svg {
      width: 48px;
      height: 48px;
      opacity: 0.4;
    }
    .empty-state p {
      font-size: 0.875rem;
      margin: 0;
    }

    /* ---- Error banner ---- */
    .error-banner {
      padding: 0.625rem 1rem;
      background: rgba(255, 59, 48, 0.08);
      color: var(--_error);
      font-size: 0.8125rem;
      text-align: center;
      border-bottom: 1px solid rgba(255, 59, 48, 0.15);
    }
  `;

  // -----------------------------------------------------------------------
  // Public reactive properties (HTML attributes)
  // -----------------------------------------------------------------------

  @property({ attribute: 'api-url' })
  apiUrl = '';

  @property()
  token = '';

  @property({ attribute: 'agent-id' })
  agentId = 'default';

  @property()
  theme: 'light' | 'dark' | 'auto' = 'light';

  @property()
  lang = 'en';

  @property({ attribute: 'conversation-id' })
  conversationId = '';

  // -----------------------------------------------------------------------
  // Internal state
  // -----------------------------------------------------------------------

  @state() private _entries: ChatEntry[] = [];
  @state() private _thinking = false;
  @state() private _thinkingTool = '';
  @state() private _connected = false;
  @state() private _connecting = false;
  @state() private _errorMessage = '';
  @state() private _inputValue = '';

  @query('.messages')
  private _messagesEl!: HTMLElement;

  private _client!: AgentAPIClient;
  private _eventSource: EventSource | null = null;
  private _entryIdCounter = 0;

  // -----------------------------------------------------------------------
  // Lifecycle
  // -----------------------------------------------------------------------

  override connectedCallback() {
    super.connectedCallback();
    this.addEventListener('user-response', this._handleComponentResponse as EventListener);
    this._boot();
  }

  override disconnectedCallback() {
    super.disconnectedCallback();
    this.removeEventListener('user-response', this._handleComponentResponse as EventListener);
    this._eventSource?.close();
  }

  // -----------------------------------------------------------------------
  // Boot sequence
  // -----------------------------------------------------------------------

  private async _boot() {
    if (!this.apiUrl) {
      this._errorMessage = 'Missing api-url attribute';
      return;
    }

    this._client = new AgentAPIClient(this.apiUrl, this.token);
    this._connecting = true;

    try {
      // Create or reuse conversation
      if (!this.conversationId) {
        const { id } = await this._client.createConversation(this.agentId);
        this.conversationId = id;
      }

      this._openStream();
      this._connected = true;
      this._connecting = false;
      this._errorMessage = '';

      this.dispatchEvent(
        new CustomEvent('agent-ready', {
          bubbles: true,
          composed: true,
          detail: { conversationId: this.conversationId },
        }),
      );
    } catch (err) {
      this._connecting = false;
      this._errorMessage = err instanceof Error ? err.message : 'Connection failed';
      this.dispatchEvent(
        new CustomEvent('agent-error', {
          bubbles: true,
          composed: true,
          detail: { error: this._errorMessage },
        }),
      );
    }
  }

  // -----------------------------------------------------------------------
  // SSE stream
  // -----------------------------------------------------------------------

  private _openStream() {
    this._eventSource?.close();
    this._eventSource = this._client.streamEvents(
      this.conversationId,
      (event) => this._handleAgentEvent(event),
      () => {
        // On SSE error, mark as disconnected and try reconnect after delay
        this._connected = false;
        setTimeout(() => {
          if (!this._connected && this.isConnected) {
            this._openStream();
          }
        }, 3000);
      },
    );
    this._connected = true;
  }

  // -----------------------------------------------------------------------
  // Event handlers
  // -----------------------------------------------------------------------

  private _handleAgentEvent(event: AgentEvent) {
    switch (event.eventType) {
      case 'token':
        this._handleToken(event.token ?? '');
        break;

      case 'component':
        if (event.component) {
          this._handleComponent(event.component);
        }
        break;

      case 'tool_start':
        this._thinking = true;
        this._thinkingTool = event.toolName ?? '';
        break;

      case 'tool_end':
        this._thinking = false;
        this._thinkingTool = '';
        break;

      case 'error':
        this._errorMessage = event.error ?? 'Unknown error';
        this._thinking = false;
        this.dispatchEvent(
          new CustomEvent('agent-error', {
            bubbles: true,
            composed: true,
            detail: { error: this._errorMessage },
          }),
        );
        break;

      case 'done':
        this._thinking = false;
        this._finaliseStreaming();
        break;
    }

    this.dispatchEvent(
      new CustomEvent('agent-response', {
        bubbles: true,
        composed: true,
        detail: event,
      }),
    );

    this._scrollToBottom();
  }

  /** Accumulate streamed tokens into a temporary streaming entry. */
  private _handleToken(token: string) {
    const last = this._entries[this._entries.length - 1];
    if (last?.streaming) {
      // Append to existing streaming entry
      const updated = [...this._entries];
      const entry = { ...last, text: (last.text ?? '') + token };
      entry.component = { type: 'message' as const, content: entry.text ?? '' };
      updated[updated.length - 1] = entry;
      this._entries = updated;
    } else {
      // Start a new streaming entry
      this._entries = [
        ...this._entries,
        {
          id: this._nextId(),
          role: 'agent',
          text: token,
          component: { type: 'message', content: token },
          streaming: true,
        },
      ];
    }
  }

  /** Mark the current streaming entry as complete. */
  private _finaliseStreaming() {
    const last = this._entries[this._entries.length - 1];
    if (last?.streaming) {
      const updated = [...this._entries];
      updated[updated.length - 1] = { ...last, streaming: false };
      this._entries = updated;
    }
  }

  /** Push a non-message UI component (form, choice-list, etc.). */
  private _handleComponent(component: UIComponent) {
    this._finaliseStreaming();
    this._entries = [
      ...this._entries,
      {
        id: this._nextId(),
        role: 'agent',
        component,
      },
    ];
  }

  /** Handle 'user-response' events from child components (form, choice, etc.). */
  private _handleComponentResponse = (e: Event) => {
    const detail = (e as CustomEvent).detail;
    if (!detail || !this.conversationId) return;

    const response: UserResponse = {
      conversationId: this.conversationId,
      ...detail,
    };

    this._client.sendMessage(this.conversationId, response).catch((err) => {
      this._errorMessage = err instanceof Error ? err.message : 'Failed to send response';
    });

    this.dispatchEvent(
      new CustomEvent('user-submitted', {
        bubbles: true,
        composed: true,
        detail: response,
      }),
    );
  };

  // -----------------------------------------------------------------------
  // User text input
  // -----------------------------------------------------------------------

  private _onInput(e: Event) {
    this._inputValue = (e.target as HTMLTextAreaElement).value;
  }

  private _onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this._sendText();
    }
  }

  private async _sendText() {
    const text = this._inputValue.trim();
    if (!text || !this.conversationId) return;

    // Add user bubble
    this._entries = [
      ...this._entries,
      {
        id: this._nextId(),
        role: 'user',
        text,
        component: { type: 'message', content: text },
      },
    ];
    this._inputValue = '';
    this._scrollToBottom();

    const response: UserResponse = {
      conversationId: this.conversationId,
      type: 'text',
      text,
    };

    try {
      await this._client.sendMessage(this.conversationId, response);
    } catch (err) {
      this._errorMessage = err instanceof Error ? err.message : 'Failed to send message';
    }

    this.dispatchEvent(
      new CustomEvent('user-submitted', {
        bubbles: true,
        composed: true,
        detail: response,
      }),
    );
  }

  // -----------------------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------------------

  private _nextId(): string {
    return `entry-${++this._entryIdCounter}`;
  }

  private _scrollToBottom() {
    requestAnimationFrame(() => {
      if (this._messagesEl) {
        this._messagesEl.scrollTop = this._messagesEl.scrollHeight;
      }
    });
  }

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------

  private _renderEntry(entry: ChatEntry) {
    if (entry.role === 'user') {
      return html`
        <div class="bubble-row user">
          <div class="bubble user">${entry.text}</div>
        </div>
      `;
    }

    // Agent entry — use the component type to decide which renderer to use
    const comp = entry.component;
    if (!comp) return nothing;

    switch (comp.type) {
      case 'message':
        return html`
          <div class="bubble-row agent">
            <div class="bubble agent">
              <chat-message .data=${comp}></chat-message>
            </div>
          </div>
        `;

      case 'form':
        return html`
          <div class="bubble-row agent">
            <div class="bubble agent component-bubble">
              <chat-form .data=${comp}></chat-form>
            </div>
          </div>
        `;

      case 'choice-list':
        return html`
          <div class="bubble-row agent">
            <div class="bubble agent component-bubble">
              <chat-choice-list .data=${comp}></chat-choice-list>
            </div>
          </div>
        `;

      case 'confirmation':
        return html`
          <div class="bubble-row agent">
            <div class="bubble agent component-bubble">
              <chat-confirmation .data=${comp}></chat-confirmation>
            </div>
          </div>
        `;

      case 'card-list':
        return html`
          <div class="bubble-row agent">
            <div class="bubble agent component-bubble">
              <chat-card-list .data=${comp}></chat-card-list>
            </div>
          </div>
        `;

      default:
        return html`
          <div class="bubble-row agent">
            <div class="bubble agent">
              <em>Unknown component type</em>
            </div>
          </div>
        `;
    }
  }

  private _renderThinking() {
    if (!this._thinking) return nothing;
    return html`
      <div class="thinking">
        <div class="thinking-dots">
          <span></span><span></span><span></span>
        </div>
        ${this._thinkingTool ? html`<span>Using ${this._thinkingTool}...</span>` : html`<span>Thinking...</span>`}
      </div>
    `;
  }

  private _connectionStatus(): 'online' | 'connecting' | 'offline' {
    if (this._connected) return 'online';
    if (this._connecting) return 'connecting';
    return 'offline';
  }

  override render() {
    const status = this._connectionStatus();

    return html`
      <!-- Header -->
      <div class="header">
        <div class="header-dot ${status === 'online' ? '' : status}"></div>
        <span class="header-title">Agent</span>
        <span class="header-status">
          ${status === 'online' ? 'Online' : status === 'connecting' ? 'Connecting...' : 'Offline'}
        </span>
      </div>

      <!-- Error banner -->
      ${this._errorMessage ? html`<div class="error-banner">${this._errorMessage}</div>` : nothing}

      <!-- Messages -->
      <div class="messages">
        ${this._entries.length === 0
          ? html`
              <div class="empty-state">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <p>Send a message to start the conversation.</p>
              </div>
            `
          : nothing}
        ${this._entries.map((entry) => this._renderEntry(entry))}
        ${this._renderThinking()}
      </div>

      <!-- Input area -->
      <div class="input-area">
        <textarea
          class="input-field"
          rows="1"
          placeholder="Type a message..."
          .value=${this._inputValue}
          @input=${this._onInput}
          @keydown=${this._onKeydown}
          ?disabled=${!this._connected}
        ></textarea>
        <button
          class="send-btn"
          @click=${this._sendText}
          ?disabled=${!this._connected || !this._inputValue.trim()}
          aria-label="Send message"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'agent-chat': AgentChat;
  }
}

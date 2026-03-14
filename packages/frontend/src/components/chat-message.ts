import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { marked } from 'marked';
import type { MessageComponent } from '../types/contracts.js';

// Configure marked for safe defaults
marked.setOptions({ async: false, breaks: true, gfm: true });

@customElement('chat-message')
export class ChatMessage extends LitElement {
  static override styles = css`
    :host {
      display: block;
    }

    .message-content {
      font-size: 0.9375rem;
      line-height: 1.65;
      color: var(--agent-text-color, #1d1d1f);
      word-wrap: break-word;
      overflow-wrap: break-word;
    }

    /* ---- Markdown prose styles ---- */
    .message-content p {
      margin: 0 0 0.75em;
    }
    .message-content p:last-child {
      margin-bottom: 0;
    }

    .message-content h1,
    .message-content h2,
    .message-content h3 {
      margin: 1em 0 0.5em;
      font-weight: 600;
      line-height: 1.3;
    }
    .message-content h1 { font-size: 1.25rem; }
    .message-content h2 { font-size: 1.125rem; }
    .message-content h3 { font-size: 1rem; }

    .message-content ul,
    .message-content ol {
      margin: 0.5em 0;
      padding-left: 1.5em;
    }

    .message-content code {
      font-family: 'SF Mono', SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 0.8375em;
      background: var(--agent-surface-color, #f5f5f7);
      padding: 0.15em 0.35em;
      border-radius: 4px;
    }

    .message-content pre {
      background: var(--agent-surface-color, #f5f5f7);
      border: 1px solid var(--agent-border-color, #e5e5ea);
      border-radius: 8px;
      padding: 0.875rem 1rem;
      overflow-x: auto;
      margin: 0.75em 0;
    }
    .message-content pre code {
      background: none;
      padding: 0;
      font-size: 0.8125rem;
    }

    .message-content blockquote {
      border-left: 3px solid var(--agent-primary-color, #0071e3);
      margin: 0.75em 0;
      padding: 0.25em 1em;
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.85;
    }

    .message-content a {
      color: var(--agent-primary-color, #0071e3);
      text-decoration: none;
    }
    .message-content a:hover {
      text-decoration: underline;
    }

    .message-content table {
      border-collapse: collapse;
      width: 100%;
      margin: 0.75em 0;
    }
    .message-content th,
    .message-content td {
      border: 1px solid var(--agent-border-color, #e5e5ea);
      padding: 0.5em 0.75em;
      text-align: left;
      font-size: 0.875rem;
    }
    .message-content th {
      background: var(--agent-surface-color, #f5f5f7);
      font-weight: 600;
    }
  `;

  @property({ type: Object })
  data!: MessageComponent;

  private _renderMarkdown(): string {
    if (!this.data?.content) return '';
    return marked.parse(this.data.content) as string;
  }

  override render() {
    return html`
      <div class="message-content">
        ${unsafeHTML(this._renderMarkdown())}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'chat-message': ChatMessage;
  }
}

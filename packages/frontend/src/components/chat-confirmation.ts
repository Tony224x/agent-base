import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import type { ConfirmationComponent } from '../types/contracts.js';

@customElement('chat-confirmation')
export class ChatConfirmation extends LitElement {
  static override styles = css`
    :host {
      display: block;
    }

    .confirm-wrapper {
      background: var(--agent-surface-color, #f5f5f7);
      border: 1px solid var(--agent-border-color, #e5e5ea);
      border-radius: var(--agent-border-radius, 12px);
      padding: 1.25rem;
    }
    .confirm-wrapper.destructive {
      border-color: var(--agent-error-color, #ff3b30);
      background: rgba(255, 59, 48, 0.04);
    }

    .confirm-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--agent-text-color, #1d1d1f);
      margin: 0 0 0.5rem;
    }
    .destructive .confirm-title {
      color: var(--agent-error-color, #ff3b30);
    }

    .confirm-message {
      font-size: 0.875rem;
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.8;
      margin: 0 0 1.25rem;
      line-height: 1.55;
    }

    .actions {
      display: flex;
      gap: 0.5rem;
      justify-content: flex-end;
    }

    button {
      font-family: inherit;
      font-size: 0.8125rem;
      font-weight: 500;
      padding: 0.5rem 1.25rem;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      transition: background-color 0.15s ease, filter 0.15s ease, transform 0.1s ease;
    }
    button:active {
      transform: scale(0.97);
    }
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-cancel {
      background: transparent;
      color: var(--agent-text-color, #1d1d1f);
      border: 1px solid var(--agent-border-color, #e5e5ea);
    }
    .btn-cancel:hover:not(:disabled) {
      background: var(--agent-border-color, #e5e5ea);
    }

    .btn-confirm {
      background: var(--agent-primary-color, #0071e3);
      color: #fff;
    }
    .btn-confirm:hover:not(:disabled) {
      filter: brightness(1.08);
    }

    .btn-confirm.destructive {
      background: var(--agent-error-color, #ff3b30);
    }

    .responded {
      font-size: 0.8125rem;
      font-weight: 500;
      padding: 0.5rem 0 0;
      text-align: right;
    }
    .responded.confirmed {
      color: var(--agent-success-color, #34c759);
    }
    .responded.cancelled {
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.5;
    }
  `;

  @property({ type: Object })
  data!: ConfirmationComponent;

  @state()
  private _responded: boolean | null = null;

  private _respond(confirmed: boolean) {
    if (this._responded !== null) return;
    this._responded = confirmed;
    this.dispatchEvent(
      new CustomEvent('user-response', {
        bubbles: true,
        composed: true,
        detail: { type: 'confirmation', confirmed },
      }),
    );
  }

  override render() {
    const d = this.data;
    if (!d) return html``;
    const destructive = d.destructive ?? false;

    return html`
      <div class="confirm-wrapper ${destructive ? 'destructive' : ''}">
        <h3 class="confirm-title">${d.title}</h3>
        <p class="confirm-message">${d.message}</p>

        ${this._responded === null
          ? html`
              <div class="actions">
                <button class="btn-cancel" @click=${() => this._respond(false)}>
                  ${d.cancelLabel ?? 'Cancel'}
                </button>
                <button class="btn-confirm ${destructive ? 'destructive' : ''}" @click=${() => this._respond(true)}>
                  ${d.confirmLabel ?? 'Confirm'}
                </button>
              </div>
            `
          : html`
              <div class="responded ${this._responded ? 'confirmed' : 'cancelled'}">
                ${this._responded ? (d.confirmLabel ?? 'Confirmed') : (d.cancelLabel ?? 'Cancelled')}
              </div>
            `}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'chat-confirmation': ChatConfirmation;
  }
}

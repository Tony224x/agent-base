import { LitElement, html, css, nothing } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import type { CardListComponent } from '../types/contracts.js';

@customElement('chat-card-list')
export class ChatCardList extends LitElement {
  static override styles = css`
    :host {
      display: block;
    }

    .card-list-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--agent-text-color, #1d1d1f);
      margin: 0 0 0.75rem;
    }

    .cards {
      display: grid;
      gap: 0.625rem;
    }

    .card {
      background: var(--agent-surface-color, #f5f5f7);
      border: 1px solid var(--agent-border-color, #e5e5ea);
      border-radius: var(--agent-border-radius, 12px);
      padding: 1rem 1.125rem;
      transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .card:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    .card-title {
      font-size: 0.9375rem;
      font-weight: 600;
      color: var(--agent-text-color, #1d1d1f);
      margin: 0;
    }

    .card-subtitle {
      font-size: 0.8125rem;
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.6;
      margin: 0.125rem 0 0;
    }

    .card-body {
      font-size: 0.8125rem;
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.8;
      margin: 0.625rem 0 0;
      line-height: 1.55;
    }

    .card-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.375rem;
      margin-top: 0.875rem;
    }

    .card-action-btn {
      font-family: inherit;
      font-size: 0.75rem;
      font-weight: 500;
      padding: 0.375rem 0.875rem;
      border-radius: 6px;
      border: 1px solid var(--agent-primary-color, #0071e3);
      background: transparent;
      color: var(--agent-primary-color, #0071e3);
      cursor: pointer;
      transition: background-color 0.15s ease, color 0.15s ease, transform 0.1s ease;
    }
    .card-action-btn:hover {
      background: var(--agent-primary-color, #0071e3);
      color: #fff;
    }
    .card-action-btn:active {
      transform: scale(0.96);
    }
  `;

  @property({ type: Object })
  data!: CardListComponent;

  private _onAction(cardId: string, actionId: string) {
    this.dispatchEvent(
      new CustomEvent('user-response', {
        bubbles: true,
        composed: true,
        detail: { type: 'card_action', cardId, cardActionId: actionId },
      }),
    );
  }

  override render() {
    if (!this.data) return nothing;

    return html`
      ${this.data.title ? html`<h3 class="card-list-title">${this.data.title}</h3>` : nothing}

      <div class="cards">
        ${this.data.cards.map(
          (card) => html`
            <div class="card">
              <h4 class="card-title">${card.title}</h4>
              ${card.subtitle ? html`<p class="card-subtitle">${card.subtitle}</p>` : nothing}
              ${card.body ? html`<p class="card-body">${card.body}</p>` : nothing}
              ${card.actions && card.actions.length > 0
                ? html`
                    <div class="card-actions">
                      ${card.actions.map(
                        (action) => html`
                          <button
                            class="card-action-btn"
                            @click=${() => this._onAction(card.id, action.actionId)}
                          >
                            ${action.label}
                          </button>
                        `,
                      )}
                    </div>
                  `
                : nothing}
            </div>
          `,
        )}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'chat-card-list': ChatCardList;
  }
}

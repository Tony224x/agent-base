import { LitElement, html, css, nothing } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import type { ChoiceListComponent } from '../types/contracts.js';

@customElement('chat-choice-list')
export class ChatChoiceList extends LitElement {
  static override styles = css`
    :host {
      display: block;
    }

    .choice-wrapper {
      background: var(--agent-surface-color, #f5f5f7);
      border: 1px solid var(--agent-border-color, #e5e5ea);
      border-radius: var(--agent-border-radius, 12px);
      padding: 1.25rem;
    }

    .choice-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--agent-text-color, #1d1d1f);
      margin: 0 0 0.25rem;
    }

    .choice-description {
      font-size: 0.8125rem;
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.7;
      margin: 0 0 1rem;
      line-height: 1.5;
    }

    .choices {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .choice-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      border: 1px solid var(--agent-border-color, #e5e5ea);
      border-radius: 8px;
      background: var(--agent-bg-color, #ffffff);
      cursor: pointer;
      transition: border-color 0.15s ease, background-color 0.15s ease,
        box-shadow 0.15s ease, transform 0.1s ease;
    }
    .choice-item:hover {
      border-color: var(--agent-primary-color, #0071e3);
      box-shadow: 0 0 0 2px rgba(0, 113, 227, 0.08);
    }
    .choice-item:active {
      transform: scale(0.985);
    }
    .choice-item.selected {
      border-color: var(--agent-primary-color, #0071e3);
      background: rgba(0, 113, 227, 0.06);
      box-shadow: 0 0 0 2px rgba(0, 113, 227, 0.15);
    }
    .choice-item.disabled {
      pointer-events: none;
      opacity: 0.5;
    }

    .choice-icon {
      font-size: 1.25rem;
      flex-shrink: 0;
    }

    .choice-text {
      flex: 1;
      min-width: 0;
    }

    .choice-label {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--agent-text-color, #1d1d1f);
    }

    .choice-desc {
      font-size: 0.75rem;
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.6;
      margin-top: 0.125rem;
    }

    .submit-row {
      margin-top: 1rem;
      display: flex;
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
      background: var(--agent-primary-color, #0071e3);
      color: #fff;
      transition: filter 0.15s ease, transform 0.1s ease;
    }
    button:hover {
      filter: brightness(1.08);
    }
    button:active {
      transform: scale(0.97);
    }
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  `;

  @property({ type: Object })
  data!: ChoiceListComponent;

  @state()
  private _selected: Set<string> = new Set();

  @state()
  private _submitted = false;

  private _toggle(id: string) {
    if (this._submitted) return;

    const next = new Set(this._selected);
    if (this.data.multiple) {
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
    } else {
      // Single select — pick and immediately submit
      next.clear();
      next.add(id);
    }
    this._selected = next;

    if (!this.data.multiple) {
      this._submit();
    }
  }

  private _submit() {
    if (this._submitted || this._selected.size === 0) return;
    this._submitted = true;
    this.dispatchEvent(
      new CustomEvent('user-response', {
        bubbles: true,
        composed: true,
        detail: {
          type: 'choice_select',
          selectedChoices: Array.from(this._selected),
        },
      }),
    );
  }

  override render() {
    if (!this.data) return nothing;

    return html`
      <div class="choice-wrapper">
        <h3 class="choice-title">${this.data.title}</h3>
        ${this.data.description ? html`<p class="choice-description">${this.data.description}</p>` : nothing}

        <div class="choices">
          ${this.data.choices.map(
            (choice) => html`
              <div
                class="choice-item ${this._selected.has(choice.id) ? 'selected' : ''} ${this._submitted ? 'disabled' : ''}"
                @click=${() => this._toggle(choice.id)}
                role="button"
                tabindex="0"
                aria-pressed=${this._selected.has(choice.id)}
                @keydown=${(e: KeyboardEvent) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this._toggle(choice.id); } }}
              >
                ${choice.icon ? html`<span class="choice-icon">${choice.icon}</span>` : nothing}
                <div class="choice-text">
                  <div class="choice-label">${choice.label}</div>
                  ${choice.description ? html`<div class="choice-desc">${choice.description}</div>` : nothing}
                </div>
              </div>
            `,
          )}
        </div>

        ${this.data.multiple
          ? html`
              <div class="submit-row">
                <button @click=${this._submit} ?disabled=${this._submitted || this._selected.size === 0}>
                  Confirm selection${this._selected.size > 0 ? ` (${this._selected.size})` : ''}
                </button>
              </div>
            `
          : nothing}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'chat-choice-list': ChatChoiceList;
  }
}

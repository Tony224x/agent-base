import { LitElement, html, css, nothing } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import type { FormComponent, FormField } from '../types/contracts.js';

@customElement('chat-form')
export class ChatForm extends LitElement {
  static override styles = css`
    :host {
      display: block;
    }

    .form-wrapper {
      background: var(--agent-surface-color, #f5f5f7);
      border: 1px solid var(--agent-border-color, #e5e5ea);
      border-radius: var(--agent-border-radius, 12px);
      padding: 1.25rem;
    }

    .form-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--agent-text-color, #1d1d1f);
      margin: 0 0 0.25rem;
    }

    .form-description {
      font-size: 0.8125rem;
      color: var(--agent-text-color, #1d1d1f);
      opacity: 0.7;
      margin: 0 0 1rem;
      line-height: 1.5;
    }

    .field-group {
      margin-bottom: 1rem;
    }
    .field-group:last-of-type {
      margin-bottom: 1.25rem;
    }

    label {
      display: block;
      font-size: 0.8125rem;
      font-weight: 500;
      color: var(--agent-text-color, #1d1d1f);
      margin-bottom: 0.35rem;
    }

    label .required {
      color: var(--agent-error-color, #ff3b30);
      margin-left: 2px;
    }

    input[type="text"],
    input[type="number"],
    input[type="email"],
    input[type="date"],
    textarea,
    select {
      width: 100%;
      font-family: inherit;
      font-size: 0.875rem;
      padding: 0.5rem 0.75rem;
      border: 1px solid var(--agent-border-color, #e5e5ea);
      border-radius: 8px;
      background: var(--agent-bg-color, #ffffff);
      color: var(--agent-text-color, #1d1d1f);
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      box-sizing: border-box;
    }
    input:focus,
    textarea:focus,
    select:focus {
      border-color: var(--agent-primary-color, #0071e3);
      box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.12);
    }

    textarea {
      min-height: 80px;
      resize: vertical;
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.875rem;
      cursor: pointer;
    }
    .checkbox-label input[type="checkbox"] {
      width: 16px;
      height: 16px;
      accent-color: var(--agent-primary-color, #0071e3);
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
      transition: background-color 0.15s ease, transform 0.1s ease;
    }
    button:active {
      transform: scale(0.97);
    }

    .btn-submit {
      background: var(--agent-primary-color, #0071e3);
      color: #fff;
    }
    .btn-submit:hover {
      filter: brightness(1.08);
    }
    .btn-submit:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-cancel {
      background: transparent;
      color: var(--agent-text-color, #1d1d1f);
      border: 1px solid var(--agent-border-color, #e5e5ea);
    }
    .btn-cancel:hover {
      background: var(--agent-border-color, #e5e5ea);
    }
  `;

  @property({ type: Object })
  data!: FormComponent;

  @state()
  private _values: Record<string, unknown> = {};

  @state()
  private _submitted = false;

  override connectedCallback() {
    super.connectedCallback();
    // Initialise default values
    if (this.data?.fields) {
      for (const field of this.data.fields) {
        if (field.defaultValue !== undefined) {
          this._values[field.name] = field.defaultValue;
        }
      }
    }
  }

  private _onInput(field: FormField, e: Event) {
    const target = e.target as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
    if (field.fieldType === 'checkbox') {
      this._values = { ...this._values, [field.name]: (target as HTMLInputElement).checked };
    } else if (field.fieldType === 'number') {
      this._values = { ...this._values, [field.name]: target.value === '' ? '' : Number(target.value) };
    } else if (field.fieldType === 'multiselect') {
      const opts = (target as HTMLSelectElement).selectedOptions;
      const selected = Array.from(opts).map((o) => o.value);
      this._values = { ...this._values, [field.name]: selected };
    } else {
      this._values = { ...this._values, [field.name]: target.value };
    }
  }

  private _onSubmit(e: Event) {
    e.preventDefault();
    if (this._submitted) return;
    this._submitted = true;
    this.dispatchEvent(
      new CustomEvent('user-response', {
        bubbles: true,
        composed: true,
        detail: { type: 'form_submit', formData: { ...this._values } },
      }),
    );
  }

  private _onCancel() {
    this.dispatchEvent(
      new CustomEvent('user-response', {
        bubbles: true,
        composed: true,
        detail: { type: 'form_submit', formData: null },
      }),
    );
  }

  private _renderField(field: FormField) {
    const val = this._values[field.name] ?? field.defaultValue ?? '';

    switch (field.fieldType) {
      case 'textarea':
        return html`<textarea
          .value=${String(val)}
          placeholder=${field.placeholder ?? ''}
          ?required=${field.required}
          ?disabled=${this._submitted}
          @input=${(e: Event) => this._onInput(field, e)}
        ></textarea>`;

      case 'select':
        return html`
          <select
            ?required=${field.required}
            ?disabled=${this._submitted}
            @change=${(e: Event) => this._onInput(field, e)}
          >
            <option value="" ?selected=${!val}>${field.placeholder ?? '-- Select --'}</option>
            ${(field.options ?? []).map(
              (o) => html`<option value=${o.value} ?selected=${val === o.value}>${o.label}</option>`,
            )}
          </select>
        `;

      case 'multiselect':
        return html`
          <select
            multiple
            ?required=${field.required}
            ?disabled=${this._submitted}
            @change=${(e: Event) => this._onInput(field, e)}
          >
            ${(field.options ?? []).map(
              (o) => html`<option value=${o.value}>${o.label}</option>`,
            )}
          </select>
        `;

      case 'checkbox':
        return html`
          <label class="checkbox-label">
            <input
              type="checkbox"
              .checked=${Boolean(val)}
              ?disabled=${this._submitted}
              @change=${(e: Event) => this._onInput(field, e)}
            />
            ${field.label}
          </label>
        `;

      default:
        return html`<input
          type=${field.fieldType}
          .value=${String(val)}
          placeholder=${field.placeholder ?? ''}
          ?required=${field.required}
          ?disabled=${this._submitted}
          @input=${(e: Event) => this._onInput(field, e)}
        />`;
    }
  }

  override render() {
    if (!this.data) return nothing;

    return html`
      <div class="form-wrapper">
        <h3 class="form-title">${this.data.title}</h3>
        ${this.data.description ? html`<p class="form-description">${this.data.description}</p>` : nothing}

        <form @submit=${this._onSubmit}>
          ${this.data.fields.map(
            (field) => html`
              <div class="field-group">
                ${field.fieldType !== 'checkbox'
                  ? html`<label>${field.label}${field.required ? html`<span class="required">*</span>` : nothing}</label>`
                  : nothing}
                ${this._renderField(field)}
              </div>
            `,
          )}

          <div class="actions">
            ${this.data.cancelLabel
              ? html`<button type="button" class="btn-cancel" @click=${this._onCancel} ?disabled=${this._submitted}>${this.data.cancelLabel}</button>`
              : nothing}
            <button type="submit" class="btn-submit" ?disabled=${this._submitted}>
              ${this.data.submitLabel ?? 'Submit'}
            </button>
          </div>
        </form>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'chat-form': ChatForm;
  }
}

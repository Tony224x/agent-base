// ---------------------------------------------------------------------------
// Component types — mirrors packages/contracts/components/*.schema.json
// ---------------------------------------------------------------------------

export type ComponentType =
  | 'message'
  | 'form'
  | 'choice-list'
  | 'confirmation'
  | 'card-list';

/** message.schema.json */
export interface MessageComponent {
  type: 'message';
  content: string;
  metadata?: Record<string, unknown>;
}

/** form.schema.json — individual field */
export interface FormFieldOption {
  label: string;
  value: string;
}

export interface FormFieldValidation {
  pattern?: string;
  min?: number;
  max?: number;
  minLength?: number;
  maxLength?: number;
}

export interface FormField {
  name: string;
  fieldType:
    | 'text'
    | 'textarea'
    | 'number'
    | 'email'
    | 'select'
    | 'multiselect'
    | 'checkbox'
    | 'date'
    | 'file';
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: FormFieldOption[];
  validation?: FormFieldValidation;
  defaultValue?: unknown;
}

/** form.schema.json */
export interface FormComponent {
  type: 'form';
  title: string;
  description?: string;
  fields: FormField[];
  submitLabel?: string;
  cancelLabel?: string;
}

/** choice-list.schema.json — individual choice */
export interface ChoiceItem {
  id: string;
  label: string;
  description?: string;
  icon?: string;
}

/** choice-list.schema.json */
export interface ChoiceListComponent {
  type: 'choice-list';
  title: string;
  description?: string;
  multiple?: boolean;
  choices: ChoiceItem[];
}

/** confirmation.schema.json */
export interface ConfirmationComponent {
  type: 'confirmation';
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
}

/** card-list.schema.json — individual card action */
export interface CardAction {
  label: string;
  actionId: string;
}

/** card-list.schema.json — individual card */
export interface Card {
  id: string;
  title: string;
  subtitle?: string;
  body?: string;
  actions?: CardAction[];
}

/** card-list.schema.json */
export interface CardListComponent {
  type: 'card-list';
  title?: string;
  cards: Card[];
}

/** Union of all renderable UI components */
export type UIComponent =
  | MessageComponent
  | FormComponent
  | ChoiceListComponent
  | ConfirmationComponent
  | CardListComponent;

// ---------------------------------------------------------------------------
// Events — mirrors packages/contracts/events/*.schema.json
// ---------------------------------------------------------------------------

export type AgentEventType =
  | 'token'
  | 'component'
  | 'tool_start'
  | 'tool_end'
  | 'error'
  | 'done';

/** agent-event.schema.json */
export interface AgentEvent {
  eventType: AgentEventType;
  conversationId: string;
  timestamp: string;
  /** Present when eventType === 'token' */
  token?: string;
  /** Present when eventType === 'component' */
  component?: UIComponent;
  /** Present when eventType === 'tool_start' | 'tool_end' */
  toolName?: string;
  /** Present when eventType === 'error' */
  error?: string;
}

// ---------------------------------------------------------------------------
// User response — mirrors packages/contracts/events/user-response.schema.json
// ---------------------------------------------------------------------------

export type UserResponseType =
  | 'text'
  | 'form_submit'
  | 'choice_select'
  | 'confirmation'
  | 'card_action';

export interface UserResponse {
  conversationId: string;
  type: UserResponseType;
  text?: string;
  formData?: Record<string, unknown>;
  selectedChoices?: string[];
  confirmed?: boolean;
  cardActionId?: string;
  cardId?: string;
}

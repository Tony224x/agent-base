# Agent Base Template — Design Spec

## Vue d'ensemble

Template monorepo pour la création d'agents IA avec LangGraph. Architecture hexagonale, backend Python (FastAPI), micro-frontend (Web Component) intégrable dans n'importe quelle app. L'agent peut pousser des composants UI dynamiques (formulaires, listes de choix, confirmations, etc.) à l'utilisateur via un protocole JSON structuré.

### Cas d'usage cibles
- Assistant IA client connecté aux MCP produits
- Assistant IA interne
- Tout agent conversationnel nécessitant des interactions UI riches

### Décisions clés
| Décision | Choix |
|---|---|
| Architecture | Monorepo avec package `contracts` partagé |
| Backend | Python, FastAPI, LangGraph, architecture hexagonale |
| Frontend | Web Component (Lit) — compatible React, Vue, Angular, vanilla JS |
| Communication agent → UI | JSON structuré (schémas dans `contracts`) |
| Temps réel | SSE (serveur → client) + REST (client → serveur) |
| Auth | Port pluggable, adapter JWT par défaut, token externe |
| Persistence | Port pluggable, adapter PostgreSQL par défaut |
| MCP | Client MCP générique derrière un port hexagonal |

---

## Structure du monorepo

```
agent-base/
├── packages/
│   ├── contracts/                 # Schémas JSON partagés (source de vérité)
│   ├── backend/                   # Python — FastAPI + LangGraph
│   └── frontend/                  # Web Component MFE (Lit)
├── docker-compose.yml             # Orchestration locale (backend + postgres + frontend dev)
├── .env.example                   # Variables d'environnement template
└── README.md
```

---

## 1. Package `contracts`

### Rôle
Source de vérité unique pour les structures de données échangées entre backend et frontend.

### Structure
```
packages/contracts/
├── components/
│   ├── message.schema.json        # Message texte simple (markdown)
│   ├── form.schema.json           # Formulaire dynamique
│   ├── choice-list.schema.json    # Liste de choix (single/multi select)
│   ├── confirmation.schema.json   # Demande de confirmation (oui/non + contexte)
│   └── card-list.schema.json      # Liste de cartes (résultats, suggestions)
├── events/
│   ├── agent-event.schema.json    # Enveloppe d'un événement agent → client (SSE)
│   └── user-response.schema.json  # Enveloppe d'une réponse client → agent (REST)
├── README.md
└── package.json                   # Publiable en npm pour le front
```

### Schémas des composants UI

#### `message.schema.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "content"],
  "properties": {
    "type": { "const": "message" },
    "content": { "type": "string", "description": "Contenu markdown" },
    "metadata": { "type": "object" }
  }
}
```

#### `form.schema.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "title", "fields"],
  "properties": {
    "type": { "const": "form" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "fields": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "fieldType", "label"],
        "properties": {
          "name": { "type": "string" },
          "fieldType": { "enum": ["text", "textarea", "number", "email", "select", "multiselect", "checkbox", "date", "file"] },
          "label": { "type": "string" },
          "placeholder": { "type": "string" },
          "required": { "type": "boolean", "default": false },
          "options": { "type": "array", "items": { "type": "object", "properties": { "label": { "type": "string" }, "value": { "type": "string" } } } },
          "validation": { "type": "object", "properties": { "pattern": { "type": "string" }, "min": { "type": "number" }, "max": { "type": "number" }, "minLength": { "type": "integer" }, "maxLength": { "type": "integer" } } },
          "defaultValue": {}
        }
      }
    },
    "submitLabel": { "type": "string", "default": "Envoyer" },
    "cancelLabel": { "type": "string" }
  }
}
```

#### `choice-list.schema.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "title", "choices"],
  "properties": {
    "type": { "const": "choice-list" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "multiple": { "type": "boolean", "default": false },
    "choices": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label"],
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "description": { "type": "string" },
          "icon": { "type": "string" }
        }
      }
    }
  }
}
```

#### `confirmation.schema.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "title", "message"],
  "properties": {
    "type": { "const": "confirmation" },
    "title": { "type": "string" },
    "message": { "type": "string" },
    "confirmLabel": { "type": "string", "default": "Confirmer" },
    "cancelLabel": { "type": "string", "default": "Annuler" },
    "destructive": { "type": "boolean", "default": false }
  }
}
```

#### `card-list.schema.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "cards"],
  "properties": {
    "type": { "const": "card-list" },
    "title": { "type": "string" },
    "cards": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "title"],
        "properties": {
          "id": { "type": "string" },
          "title": { "type": "string" },
          "subtitle": { "type": "string" },
          "body": { "type": "string" },
          "actions": { "type": "array", "items": { "type": "object", "properties": { "label": { "type": "string" }, "actionId": { "type": "string" } } } }
        }
      }
    }
  }
}
```

### Schémas des événements

#### `agent-event.schema.json` (SSE)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["eventType", "conversationId", "timestamp"],
  "properties": {
    "eventType": { "enum": ["token", "component", "tool_start", "tool_end", "error", "done"] },
    "conversationId": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "token": { "type": "string", "description": "Pour eventType=token, le token streamé" },
    "component": { "$ref": "#/definitions/UIComponent", "description": "Pour eventType=component" },
    "toolName": { "type": "string", "description": "Pour eventType=tool_start|tool_end" },
    "error": { "type": "string", "description": "Pour eventType=error" }
  },
  "definitions": {
    "UIComponent": {
      "oneOf": [
        { "$ref": "message.schema.json" },
        { "$ref": "form.schema.json" },
        { "$ref": "choice-list.schema.json" },
        { "$ref": "confirmation.schema.json" },
        { "$ref": "card-list.schema.json" }
      ]
    }
  }
}
```

#### `user-response.schema.json` (REST)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["conversationId", "type"],
  "properties": {
    "conversationId": { "type": "string" },
    "type": { "enum": ["text", "form_submit", "choice_select", "confirmation", "card_action"] },
    "text": { "type": "string" },
    "formData": { "type": "object" },
    "selectedChoices": { "type": "array", "items": { "type": "string" } },
    "confirmed": { "type": "boolean" },
    "cardActionId": { "type": "string" },
    "cardId": { "type": "string" }
  }
}
```

---

## 2. Backend — Architecture hexagonale

### Structure complète
```
packages/backend/
├── src/
│   ├── domain/
│   │   ├── models/
│   │   │   ├── conversation.py      # Conversation, Message, UIComponentPayload
│   │   │   └── agent_config.py      # AgentConfig (nom, system prompt, tools autorisés)
│   │   ├── ports/
│   │   │   ├── llm.py               # Protocol LLMPort: chat(), stream()
│   │   │   ├── persistence.py       # Protocol PersistencePort: save/load conversation + graph state
│   │   │   ├── tools.py             # Protocol ToolsPort: discover(), execute()
│   │   │   └── auth.py              # Protocol AuthPort: validate_token() → UserContext
│   │   └── services/
│   │       ├── agent_service.py     # Orchestre le graph, valide les UI components vs contracts
│   │       └── contract_validator.py # Valide les payloads JSON contre les schémas contracts
│   │
│   ├── adapters/
│   │   ├── llm/
│   │   │   └── langchain_adapter.py # LangChain ChatModel (OpenAI, Anthropic, etc.)
│   │   ├── persistence/
│   │   │   ├── postgres_adapter.py  # SQLAlchemy + LangGraph checkpointer Postgres
│   │   │   └── memory_adapter.py    # Dict in-memory (dev/tests)
│   │   ├── tools/
│   │   │   └── mcp_adapter.py       # Client MCP générique (découverte + exécution via config)
│   │   └── auth/
│   │       └── jwt_adapter.py       # Validation JWT, extraction UserContext
│   │
│   ├── graph/
│   │   ├── state.py                 # AgentState(TypedDict): messages, pending_ui, tool_results
│   │   ├── nodes/
│   │   │   ├── chat_node.py         # Appel LLM via port
│   │   │   ├── tool_node.py         # Exécution tool via port
│   │   │   └── ui_push_node.py      # Construction + validation composant UI
│   │   ├── edges.py                 # should_use_tool(), should_push_ui(), is_done()
│   │   └── builder.py              # build_graph(config) → CompiledGraph
│   │
│   └── api/
│       ├── app.py                   # FastAPI app factory
│       ├── routes/
│       │   ├── chat.py              # POST /conversations/{id}/messages + GET .../stream
│       │   ├── conversations.py     # CRUD conversations
│       │   └── health.py            # GET /health
│       ├── middleware/
│       │   └── auth_middleware.py    # Utilise AuthPort
│       └── dependencies.py          # Injection: ports → adapters (configurable via env)
│
├── config/
│   ├── agents/                      # Fichiers YAML de config agent
│   │   └── default.yaml             # system_prompt, model, tools, ui_components autorisés
│   └── mcp_servers.yaml             # Liste des serveurs MCP à connecter
│
├── tests/
│   ├── unit/
│   │   ├── domain/                  # Tests du domaine (ports mockés)
│   │   └── graph/                   # Tests des nodes et edges
│   └── integration/
│       └── adapters/                # Tests avec vrais adapters
│
├── alembic/                         # Migrations DB
├── pyproject.toml
└── Dockerfile
```

### Ports (interfaces)

```python
# domain/ports/llm.py
from typing import Protocol, AsyncIterator
from domain.models.conversation import Message

class LLMPort(Protocol):
    async def chat(self, messages: list[Message], model: str) -> Message: ...
    async def stream(self, messages: list[Message], model: str) -> AsyncIterator[str]: ...

# domain/ports/tools.py
class ToolsPort(Protocol):
    async def discover(self) -> list[ToolDefinition]: ...
    async def execute(self, tool_name: str, arguments: dict) -> ToolResult: ...

# domain/ports/persistence.py
class PersistencePort(Protocol):
    async def save_conversation(self, conversation: Conversation) -> None: ...
    async def load_conversation(self, conversation_id: str) -> Conversation | None: ...
    async def save_graph_state(self, conversation_id: str, state: dict) -> None: ...
    async def load_graph_state(self, conversation_id: str) -> dict | None: ...

# domain/ports/auth.py
class AuthPort(Protocol):
    async def validate_token(self, token: str) -> UserContext | None: ...
```

### LangGraph — State & Nodes

```python
# graph/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Historique conversation
    pending_ui: list[dict] | None            # Composants UI à pousser
    tool_calls: list[dict] | None            # Tools à exécuter
    user_context: dict                       # Info user (du token)
    agent_config: dict                       # Config agent active

# graph/nodes/ui_push_node.py
async def ui_push_node(state: AgentState) -> dict:
    """Construit un composant UI depuis la décision du LLM."""
    # Le LLM a retourné un tool_call spécial "push_ui"
    # On valide le payload contre les schémas contracts/
    # On le met dans pending_ui pour que l'API le streame via SSE
    ...

# graph/edges.py
def route_after_llm(state: AgentState) -> str:
    last = state["messages"][-1]
    if has_tool_calls(last):
        if is_ui_push(last):
            return "ui_push"
        return "tool_executor"
    return END
```

### Graph structure

```
                    ┌──────────────┐
                    │    START     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
              ┌─────│   chat_node  │─────┐
              │     └──────────────┘     │
              │            │             │
       tool_call?      ui_push?       done?
              │            │             │
     ┌────────▼───┐  ┌─────▼──────┐     │
     │ tool_node  │  │ ui_push    │     │
     └────────┬───┘  └─────┬──────┘     │
              │            │             │
              └────────────┘             │
                    │                    │
              (back to chat)       ┌─────▼───┐
                                   │   END   │
                                   └─────────┘
```

### Configuration agent (YAML)

```yaml
# config/agents/default.yaml
name: "default-assistant"
model: "gpt-4o"
system_prompt: |
  Tu es un assistant IA. Tu peux répondre en texte ou pousser
  des composants UI quand c'est pertinent.

  Composants UI disponibles : form, choice-list, confirmation, card-list.

  Pour pousser un composant UI, utilise le tool push_ui avec le payload JSON.

allowed_tools:
  - "*"  # Tous les tools MCP découverts

allowed_ui_components:
  - "form"
  - "choice-list"
  - "confirmation"
  - "card-list"
  - "message"

max_turns: 20
temperature: 0.7
```

### API Routes

```
POST   /api/conversations                    # Créer une conversation
GET    /api/conversations/{id}               # Récupérer une conversation
DELETE /api/conversations/{id}               # Supprimer

POST   /api/conversations/{id}/messages      # Envoyer un message (ou réponse UI)
  Body: user-response.schema.json
  Response: 201 + conversation_id

GET    /api/conversations/{id}/stream        # SSE stream des événements agent
  Events: agent-event.schema.json
  Types: token | component | tool_start | tool_end | error | done
```

### Sécurité

- **Input validation** : tous les inputs utilisateur validés via Pydantic
- **Prompt injection** : le system prompt utilise des délimiteurs XML pour séparer instructions système / input user
- **Auth** : middleware vérifie le token sur chaque requête, extrait le UserContext
- **Tools** : least privilege — chaque config agent déclare les tools autorisés
- **PII** : le port de persistence ne log jamais le contenu des messages en clair (configurable)

---

## 3. Frontend — Micro-Frontend Web Component

### Stack
- **Lit** (Web Components) — léger (~5kb), standard, compatible partout
- **TypeScript**
- Build: **Vite**
- Publiable en npm ou servable en CDN

### Structure
```
packages/frontend/
├── src/
│   ├── agent-chat.ts              # Composant principal <agent-chat>
│   ├── components/
│   │   ├── chat-message.ts        # Rendu d'un message (markdown)
│   │   ├── chat-form.ts           # Rendu d'un formulaire dynamique
│   │   ├── chat-choice-list.ts    # Rendu d'une liste de choix
│   │   ├── chat-confirmation.ts   # Rendu d'une confirmation
│   │   ├── chat-card-list.ts      # Rendu d'une liste de cartes
│   │   └── component-registry.ts  # Map type → composant (extensible)
│   ├── services/
│   │   ├── api-client.ts          # Client REST + SSE
│   │   └── event-parser.ts        # Parse les événements SSE
│   ├── styles/
│   │   ├── tokens.css             # Design tokens (CSS custom properties)
│   │   └── base.css               # Styles de base
│   └── types/
│       └── contracts.ts           # Types TS générés depuis contracts/
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html                     # Page de dev/démo
```

### Intégration dans une app hôte

```html
<!-- Charger le bundle -->
<script type="module" src="https://cdn.example.com/agent-chat/agent-chat.js"></script>

<!-- Utiliser le Web Component -->
<agent-chat
  api-url="https://api.example.com"
  token="eyJhbG..."
  agent-id="default-assistant"
  theme="light"
  lang="fr"
></agent-chat>
```

### Attributs/propriétés du Web Component

| Attribut | Type | Description |
|---|---|---|
| `api-url` | string | URL du backend |
| `token` | string | Token auth (JWT) |
| `agent-id` | string | ID de la config agent à utiliser |
| `theme` | "light" \| "dark" \| "auto" | Thème visuel |
| `lang` | string | Langue (i18n) |
| `conversation-id` | string? | Reprendre une conversation existante |

### Events émis (vers l'app hôte)

| Event | Detail | Quand |
|---|---|---|
| `agent-ready` | `{}` | Connexion SSE établie |
| `agent-response` | `{ component }` | L'agent a poussé un composant |
| `user-submitted` | `{ response }` | L'utilisateur a soumis une réponse |
| `agent-error` | `{ error }` | Erreur de l'agent |

L'app hôte peut écouter ces events pour réagir (analytics, logs, navigation, etc.).

### Component Registry (extensibilité)

```typescript
// component-registry.ts
const registry = new Map<string, typeof LitElement>();

// Composants par défaut
registry.set('message', ChatMessage);
registry.set('form', ChatForm);
registry.set('choice-list', ChatChoiceList);
registry.set('confirmation', ChatConfirmation);
registry.set('card-list', ChatCardList);

// L'app hôte peut enregistrer des composants custom
export function registerComponent(type: string, component: typeof LitElement) {
  registry.set(type, component);
}
```

### Theming

Le MFE utilise des **CSS custom properties** pour le theming. L'app hôte peut les surcharger :

```css
agent-chat {
  --agent-primary-color: #2563eb;
  --agent-bg-color: #ffffff;
  --agent-text-color: #1f2937;
  --agent-border-radius: 8px;
  --agent-font-family: 'Inter', sans-serif;
}
```

---

## 4. Infrastructure & DX

### docker-compose.yml
```yaml
services:
  backend:
    build: ./packages/backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres]

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: agent_base
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: agent_dev
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  frontend:
    build: ./packages/frontend
    ports: ["3000:3000"]

volumes:
  pgdata:
```

### .env.example
```env
# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql+asyncpg://agent:agent_dev@localhost:5432/agent_base

# Auth
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256

# MCP
MCP_CONFIG_PATH=config/mcp_servers.yaml

# Agent
DEFAULT_AGENT_CONFIG=config/agents/default.yaml
```

### Flux complet — Exemple

1. L'utilisateur tape "Je veux créer un ticket support" dans `<agent-chat>`
2. Le MFE envoie `POST /api/conversations/{id}/messages` avec `{ type: "text", text: "Je veux créer un ticket support" }`
3. Le MFE ouvre `GET /api/conversations/{id}/stream` (SSE)
4. Le backend exécute le graph LangGraph :
   - `chat_node` : le LLM décide de pousser un formulaire
   - `ui_push_node` : construit le payload `form`, le valide contre `form.schema.json`
5. Le backend streame un event SSE : `{ eventType: "component", component: { type: "form", title: "Créer un ticket", fields: [...] } }`
6. Le MFE reçoit l'event, lit `type: "form"`, consulte le registry, rend `<chat-form>`
7. L'utilisateur remplit et soumet le formulaire
8. Le MFE envoie `POST /api/conversations/{id}/messages` avec `{ type: "form_submit", formData: { subject: "Bug login", priority: "high" } }`
9. Le graph reprend — le LLM peut appeler un tool MCP pour créer le ticket dans le système cible
10. L'agent confirme la création via un event `component` de type `message`

---

## 5. Extensibilité — Comment créer un nouvel agent

Pour créer un agent spécialisé à partir de ce template :

1. **Créer un fichier de config** `config/agents/mon-agent.yaml` (system prompt, tools autorisés, etc.)
2. **Configurer les serveurs MCP** dans `config/mcp_servers.yaml`
3. **(Optionnel) Ajouter un composant UI custom** dans `contracts/` + front `component-registry`
4. Déployer avec `agent-id="mon-agent"` dans le Web Component

Pas besoin de toucher au code du template pour les cas standards.

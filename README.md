# Agent Base

Template monorepo production-ready pour créer des agents IA conversationnels avec **LangGraph**, une **architecture hexagonale**, et un **micro-frontend Web Component** intégrable dans n'importe quelle application.

L'agent peut streamer du texte en temps réel et pousser des composants UI interactifs (formulaires, listes de choix, confirmations, cartes) à l'utilisateur via un protocole JSON structuré.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Lit)                        │
│              <agent-chat> Web Component                 │
│         SSE streaming  ·  Dynamic UI rendering          │
└──────────────────────┬──────────────────────────────────┘
                       │ REST + SSE
┌──────────────────────▼──────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │                   Use Cases                        │  │
│  │   AskQuestion · ManageConversations · Extract...   │  │
│  └────────────┬───────────────────────────────────────┘  │
│  ┌────────────▼───────────────────────────────────────┐  │
│  │              Domain (Ports & Adapters)              │  │
│  │  LLMPort · ToolsPort · AuthPort · Repository       │  │
│  └────────────┬───────────────────────────────────────┘  │
│  ┌────────────▼───────────────────────────────────────┐  │
│  │               LangGraph State Machine              │  │
│  │     chat_node → tool_node / ui_push_node → END     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      PostgreSQL    LLM APIs    MCP Servers
                  (OpenAI,     (outils externes)
                  Anthropic,
                  Bedrock)
```

## Fonctionnalités

- **Streaming temps réel** — SSE avec tokens, composants UI, et cycle de vie des outils
- **Composants UI dynamiques** — Formulaires, listes de choix, confirmations, grilles de cartes
- **Multi-LLM** — OpenAI, Anthropic, AWS Bedrock via LangChain
- **MCP Tools** — Extension des capacités de l'agent via Model Context Protocol
- **Architecture hexagonale** — Domaine isolé, ports explicites, adaptateurs interchangeables
- **Web Component** — Drop-in `<agent-chat>`, compatible React / Angular / Vue / vanilla JS
- **Contrats typés** — JSON Schemas partagés entre frontend et backend
- **Auth JWT** — Middleware d'authentification intégré
- **Persistance** — Conversations et state graph sauvegardés en PostgreSQL

## Structure du projet

```
agent-base/
├── packages/
│   ├── backend/              # FastAPI + LangGraph
│   │   └── src/
│   │       ├── core/
│   │       │   ├── domain/   # Entités, value objects, services
│   │       │   ├── ports/    # Interfaces inbound & outbound
│   │       │   ├── use_cases/# Logique métier
│   │       │   └── graph/    # LangGraph (state, nodes, edges)
│   │       ├── adapters/
│   │       │   ├── inbound/  # API FastAPI (routes, middleware)
│   │       │   └── outbound/ # LLM, DB, Auth, MCP adapters
│   │       └── main.py
│   │
│   ├── frontend/             # Lit Web Components
│   │   └── src/
│   │       ├── agent-chat.ts # Composant principal
│   │       ├── components/   # chat-form, chat-choice-list, etc.
│   │       └── services/     # API client, SSE parser
│   │
│   └── contracts/            # JSON Schemas partagés
│       └── schemas/
│           ├── components/   # form, choice-list, confirmation, card-list
│           └── events/       # agent-event, user-response
│
├── docker-compose.yml
├── .env.example
└── LICENSE
```

## Quick Start

### Prérequis

- Docker & Docker Compose
- Une clé API LLM (OpenAI ou Anthropic)

### Lancement

```bash
# 1. Cloner le repo
git clone https://github.com/Tony224x/agent-base.git
cd agent-base

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec votre clé API

# 3. Lancer les services
docker compose up
```

Le backend sera disponible sur `http://localhost:8000` et le frontend sur `http://localhost:3000`.

### Configuration

Variables d'environnement principales (`.env`) :

| Variable | Description | Défaut |
|----------|-------------|--------|
| `LLM_PROVIDER` | Provider LLM (`openai`, `anthropic`) | `openai` |
| `OPENAI_API_KEY` | Clé API OpenAI | — |
| `ANTHROPIC_API_KEY` | Clé API Anthropic | — |
| `DATABASE_URL` | URL PostgreSQL async | `postgresql+asyncpg://agent:agent_dev@localhost:5432/agent_base` |
| `JWT_SECRET` | Secret pour les tokens JWT | `change-me-in-production` |
| `MCP_CONFIG_PATH` | Chemin vers la config MCP servers | `config/mcp_servers.yaml` |

## Utilisation

### Intégrer le Web Component

```html
<script type="module" src="https://your-cdn.com/agent-chat.js"></script>

<agent-chat
  api-url="http://localhost:8000"
  token="your-jwt-token"
  agent-id="default"
  theme="auto"
></agent-chat>
```

### API Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/conversations` | Créer une conversation |
| `GET` | `/api/conversations/{id}` | Récupérer une conversation |
| `POST` | `/api/conversations/{id}/messages` | Envoyer un message |
| `GET` | `/api/conversations/{id}/events` | Stream SSE des événements |

### Événements SSE

Le stream SSE émet les événements suivants :

| Type | Description |
|------|-------------|
| `token` | Token de texte streamé par le LLM |
| `component` | Composant UI à rendre (form, choice-list, etc.) |
| `tool_start` | Début d'exécution d'un outil |
| `tool_end` | Fin d'exécution d'un outil |
| `error` | Erreur survenue |
| `done` | Réponse complète |

## Composants UI supportés

L'agent peut pousser ces composants interactifs au frontend :

| Composant | Description | Champs supportés |
|-----------|-------------|-----------------|
| **Form** | Formulaire dynamique | text, textarea, number, email, select, multiselect, checkbox, date, file |
| **Choice List** | Liste de choix multiples | Sélection simple ou multiple avec descriptions |
| **Confirmation** | Dialogue de confirmation | Oui / Non avec message personnalisé |
| **Card List** | Grille de cartes | Titre, description, image, actions |

## Configurer l'agent

L'agent se configure via `config/agents/default.yaml` :

```yaml
model: gpt-4o
temperature: 0.7
system_prompt: |
  Tu es un assistant IA. Tu peux utiliser des composants UI
  pour interagir avec l'utilisateur (formulaires, listes, etc.)
allowed_tools: ["*"]
max_turns: 20
```

## Ajouter des outils MCP

Configurer les serveurs MCP dans `config/mcp_servers.yaml` :

```yaml
servers:
  - name: my-tool-server
    command: npx
    args: ["-y", "@my-org/mcp-server"]
    env:
      API_KEY: "${MY_TOOL_API_KEY}"
```

## Développement

### Backend

```bash
cd packages/backend
pip install -e ".[dev]"
pytest
```

### Frontend

```bash
cd packages/frontend
npm install
npm run dev     # Serveur de dev
npm run build   # Build production
```

## Stack technique

| Couche | Technologies |
|--------|-------------|
| **Backend** | Python 3.12, FastAPI, LangGraph, LangChain, SQLAlchemy 2.0, Pydantic 2, Alembic |
| **Frontend** | TypeScript, Lit 3, Vite 6, Marked |
| **Infrastructure** | PostgreSQL 16, Docker, SSE |
| **Protocoles** | MCP (Model Context Protocol), JWT, JSON Schema |

## Licence

Ce projet est sous licence [CC BY-NC 4.0](LICENSE) — usage non-commercial uniquement.

Attribution requise : **VON BIELER Anthony** — [github.com/Tony224x](https://github.com/Tony224x)

Pour un usage commercial, contactez l'auteur.

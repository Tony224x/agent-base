# Agent Base Template — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-ready monorepo template for AI agents with LangGraph, hexagonal architecture, and a Web Component MFE that renders dynamic UI pushed by the agent.

**Architecture:** Monorepo with 3 packages (contracts, backend, frontend). Backend uses hexagonal architecture (ports/adapters) with LangGraph for agent orchestration. Frontend is a Lit Web Component communicating via SSE + REST. Shared JSON schemas in contracts package ensure type safety across the stack.

**Tech Stack:** Python 3.12, FastAPI, LangGraph, SQLAlchemy, Alembic, Pydantic | TypeScript, Lit, Vite | PostgreSQL, Docker

---

## Phase 1: Monorepo Scaffolding & Contracts

### Task 1: Root monorepo structure

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `README.md`

**Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/
venv/
.env

# Node
node_modules/
packages/frontend/dist/

# IDE
.vscode/
.idea/

# Docker
pgdata/

# OS
.DS_Store
Thumbs.db
```

**Step 2: Create .env.example**

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

**Step 3: Create docker-compose.yml**

```yaml
services:
  backend:
    build: ./packages/backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres]
    volumes:
      - ./packages/backend/src:/app/src
      - ./packages/contracts:/app/contracts

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
      - ./packages/frontend/src:/app/src

volumes:
  pgdata:
```

**Step 4: Commit**

```bash
git add .gitignore .env.example docker-compose.yml
git commit -m "chore: scaffold monorepo root with docker-compose"
```

---

### Task 2: Contracts package — JSON schemas

**Files:**
- Create: `packages/contracts/package.json`
- Create: `packages/contracts/components/message.schema.json`
- Create: `packages/contracts/components/form.schema.json`
- Create: `packages/contracts/components/choice-list.schema.json`
- Create: `packages/contracts/components/confirmation.schema.json`
- Create: `packages/contracts/components/card-list.schema.json`
- Create: `packages/contracts/events/agent-event.schema.json`
- Create: `packages/contracts/events/user-response.schema.json`

**Step 1: Create package.json**

```json
{
  "name": "@agent-base/contracts",
  "version": "0.1.0",
  "description": "Shared JSON schemas for agent-base UI components and events",
  "main": "index.js",
  "files": ["components/", "events/"]
}
```

**Step 2: Create all 5 component schemas**

Copy exact schemas from design spec:
- `message.schema.json` — type: message, required: [type, content]
- `form.schema.json` — type: form, required: [type, title, fields], fields with fieldType enum
- `choice-list.schema.json` — type: choice-list, required: [type, title, choices]
- `confirmation.schema.json` — type: confirmation, required: [type, title, message]
- `card-list.schema.json` — type: card-list, required: [type, cards]

**Step 3: Create event schemas**

- `agent-event.schema.json` — eventType enum: [token, component, tool_start, tool_end, error, done]
- `user-response.schema.json` — type enum: [text, form_submit, choice_select, confirmation, card_action]

**Step 4: Validate schemas are valid JSON**

Run: `python -c "import json, pathlib; [json.loads(f.read_text()) for f in pathlib.Path('packages/contracts').rglob('*.json') if f.name != 'package.json']; print('All schemas valid')"`

Expected: `All schemas valid`

**Step 5: Commit**

```bash
git add packages/contracts/
git commit -m "feat(contracts): add JSON schemas for UI components and events"
```

---

## Phase 2: Backend Domain (Pure Python, Zero Dependencies)

### Task 3: Backend project setup

**Files:**
- Create: `packages/backend/pyproject.toml`
- Create: `packages/backend/src/__init__.py`
- Create: `packages/backend/src/domain/__init__.py`
- Create: `packages/backend/src/domain/models/__init__.py`
- Create: `packages/backend/src/domain/ports/__init__.py`
- Create: `packages/backend/src/domain/services/__init__.py`
- Create: `packages/backend/Dockerfile`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "agent-base-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "langchain-core>=0.3.0",
    "langchain-openai>=0.3.0",
    "langgraph>=0.3.0",
    "langgraph-checkpoint-postgres>=2.0.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pyjwt>=2.10.0",
    "jsonschema>=4.23.0",
    "pyyaml>=6.0.0",
    "sse-starlette>=2.2.0",
    "mcp>=1.0.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.25.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.9.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

**Step 2: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY src/ src/
COPY config/ config/

CMD ["uvicorn", "src.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Step 3: Create all __init__.py files**

Empty `__init__.py` for: `src/`, `src/domain/`, `src/domain/models/`, `src/domain/ports/`, `src/domain/services/`

**Step 4: Commit**

```bash
git add packages/backend/
git commit -m "chore(backend): scaffold project with pyproject.toml and Dockerfile"
```

---

### Task 4: Domain models

**Files:**
- Create: `packages/backend/src/domain/models/conversation.py`
- Create: `packages/backend/src/domain/models/agent_config.py`
- Test: `packages/backend/tests/unit/domain/test_models.py`

**Step 1: Write failing tests**

```python
# tests/unit/domain/test_models.py
from src.domain.models.conversation import Conversation, Message, Role, UIComponentPayload
from src.domain.models.agent_config import AgentConfig

def test_message_creation():
    msg = Message(role=Role.USER, content="hello")
    assert msg.role == Role.USER
    assert msg.content == "hello"

def test_conversation_add_message():
    conv = Conversation(agent_id="default")
    conv.add_message(Message(role=Role.USER, content="hi"))
    assert len(conv.messages) == 1

def test_ui_component_payload():
    payload = UIComponentPayload(component_type="form", data={"title": "Test", "fields": []})
    assert payload.component_type == "form"

def test_agent_config_loading():
    config = AgentConfig(
        name="test",
        model="gpt-4o",
        system_prompt="You are a test agent.",
        allowed_tools=["*"],
        allowed_ui_components=["form", "message"],
        max_turns=20,
        temperature=0.7,
    )
    assert config.name == "test"
    assert config.allows_ui_component("form") is True
    assert config.allows_ui_component("unknown") is False
```

**Step 2: Run test to verify it fails**

Run: `cd packages/backend && pip install -e ".[dev]" && pytest tests/unit/domain/test_models.py -v`
Expected: FAIL — modules not found

**Step 3: Implement conversation.py**

```python
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    role: Role
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None


@dataclass
class UIComponentPayload:
    component_type: str
    data: dict


@dataclass
class Conversation:
    agent_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
```

**Step 4: Implement agent_config.py**

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    name: str
    model: str
    system_prompt: str
    allowed_tools: list[str] = field(default_factory=lambda: ["*"])
    allowed_ui_components: list[str] = field(default_factory=list)
    max_turns: int = 20
    temperature: float = 0.7

    def allows_tool(self, tool_name: str) -> bool:
        return "*" in self.allowed_tools or tool_name in self.allowed_tools

    def allows_ui_component(self, component_type: str) -> bool:
        return component_type in self.allowed_ui_components
```

**Step 5: Run tests**

Run: `cd packages/backend && pytest tests/unit/domain/test_models.py -v`
Expected: all PASS

**Step 6: Commit**

```bash
git add packages/backend/src/domain/models/ packages/backend/tests/
git commit -m "feat(backend): add domain models — Conversation, Message, AgentConfig"
```

---

### Task 5: Domain ports (interfaces)

**Files:**
- Create: `packages/backend/src/domain/ports/llm.py`
- Create: `packages/backend/src/domain/ports/persistence.py`
- Create: `packages/backend/src/domain/ports/tools.py`
- Create: `packages/backend/src/domain/ports/auth.py`

**Step 1: Implement all 4 port protocols**

```python
# domain/ports/llm.py
from typing import Protocol, AsyncIterator
from src.domain.models.conversation import Message

class LLMPort(Protocol):
    async def chat(self, messages: list[Message], model: str) -> Message: ...
    async def stream(self, messages: list[Message], model: str) -> AsyncIterator[str]: ...
```

```python
# domain/ports/persistence.py
from typing import Protocol
from src.domain.models.conversation import Conversation

class PersistencePort(Protocol):
    async def save_conversation(self, conversation: Conversation) -> None: ...
    async def load_conversation(self, conversation_id: str) -> Conversation | None: ...
    async def list_conversations(self, user_id: str) -> list[Conversation]: ...
    async def delete_conversation(self, conversation_id: str) -> bool: ...
    async def save_graph_state(self, conversation_id: str, state: dict) -> None: ...
    async def load_graph_state(self, conversation_id: str) -> dict | None: ...
```

```python
# domain/ports/tools.py
from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict

@dataclass
class ToolResult:
    tool_name: str
    result: str
    is_error: bool = False

class ToolsPort(Protocol):
    async def discover(self) -> list[ToolDefinition]: ...
    async def execute(self, tool_name: str, arguments: dict) -> ToolResult: ...
```

```python
# domain/ports/auth.py
from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass

@dataclass
class UserContext:
    user_id: str
    tenant_id: str | None = None
    roles: list[str] | None = None
    metadata: dict | None = None

class AuthPort(Protocol):
    async def validate_token(self, token: str) -> UserContext | None: ...
```

**Step 2: Commit**

```bash
git add packages/backend/src/domain/ports/
git commit -m "feat(backend): add domain ports — LLM, Persistence, Tools, Auth"
```

---

### Task 6: Contract validator service

**Files:**
- Create: `packages/backend/src/domain/services/contract_validator.py`
- Test: `packages/backend/tests/unit/domain/test_contract_validator.py`

**Step 1: Write failing tests**

```python
# tests/unit/domain/test_contract_validator.py
import pytest
from src.domain.services.contract_validator import ContractValidator

@pytest.fixture
def validator():
    return ContractValidator(schemas_dir="../../contracts")

def test_validate_message_component(validator):
    payload = {"type": "message", "content": "Hello world"}
    assert validator.validate_component(payload) is True

def test_validate_form_component(validator):
    payload = {
        "type": "form",
        "title": "Test Form",
        "fields": [{"name": "email", "fieldType": "email", "label": "Email"}],
    }
    assert validator.validate_component(payload) is True

def test_reject_invalid_component(validator):
    payload = {"type": "form"}  # missing required fields
    with pytest.raises(ValueError):
        validator.validate_component(payload)

def test_reject_unknown_type(validator):
    payload = {"type": "unknown_widget", "data": {}}
    with pytest.raises(ValueError, match="Unknown component type"):
        validator.validate_component(payload)
```

**Step 2: Implement ContractValidator**

```python
from __future__ import annotations

import json
from pathlib import Path
from jsonschema import validate, ValidationError


class ContractValidator:
    def __init__(self, schemas_dir: str | Path) -> None:
        self._schemas_dir = Path(schemas_dir)
        self._schemas: dict[str, dict] = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        components_dir = self._schemas_dir / "components"
        if not components_dir.exists():
            return
        for schema_file in components_dir.glob("*.schema.json"):
            schema = json.loads(schema_file.read_text(encoding="utf-8"))
            # Extract type from schema const
            type_name = schema.get("properties", {}).get("type", {}).get("const")
            if type_name:
                self._schemas[type_name] = schema

    def validate_component(self, payload: dict) -> bool:
        component_type = payload.get("type")
        if component_type not in self._schemas:
            raise ValueError(f"Unknown component type: {component_type}")
        try:
            validate(instance=payload, schema=self._schemas[component_type])
        except ValidationError as e:
            raise ValueError(f"Invalid {component_type} component: {e.message}") from e
        return True

    def get_known_types(self) -> list[str]:
        return list(self._schemas.keys())
```

**Step 3: Run tests**

Run: `cd packages/backend && pytest tests/unit/domain/test_contract_validator.py -v`
Expected: all PASS

**Step 4: Commit**

```bash
git add packages/backend/src/domain/services/ packages/backend/tests/
git commit -m "feat(backend): add ContractValidator — validates UI payloads against schemas"
```

---

## Phase 3: LangGraph Agent Graph

### Task 7: Graph state definition

**Files:**
- Create: `packages/backend/src/graph/__init__.py`
- Create: `packages/backend/src/graph/state.py`
- Test: `packages/backend/tests/unit/graph/test_state.py`

**Step 1: Write failing test**

```python
# tests/unit/graph/test_state.py
from src.graph.state import AgentState

def test_agent_state_is_typed_dict():
    state: AgentState = {
        "messages": [],
        "pending_ui": None,
        "tool_calls": None,
        "user_context": {"user_id": "u1"},
        "agent_config": {"name": "test"},
    }
    assert state["messages"] == []
    assert state["pending_ui"] is None
```

**Step 2: Implement state.py**

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    pending_ui: list[dict] | None
    tool_calls: list[dict] | None
    user_context: dict
    agent_config: dict
```

**Step 3: Run tests, commit**

```bash
git commit -m "feat(backend): add LangGraph AgentState definition"
```

---

### Task 8: Graph nodes

**Files:**
- Create: `packages/backend/src/graph/nodes/__init__.py`
- Create: `packages/backend/src/graph/nodes/chat_node.py`
- Create: `packages/backend/src/graph/nodes/tool_node.py`
- Create: `packages/backend/src/graph/nodes/ui_push_node.py`
- Test: `packages/backend/tests/unit/graph/test_nodes.py`

**Step 1: Write failing tests**

```python
# tests/unit/graph/test_nodes.py
import pytest
from unittest.mock import AsyncMock
from src.graph.nodes.chat_node import make_chat_node
from src.graph.nodes.tool_node import make_tool_node
from src.graph.nodes.ui_push_node import make_ui_push_node

@pytest.mark.asyncio
async def test_chat_node_returns_messages():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AIMessage(content="Hello!")
    chat = make_chat_node(mock_llm)
    state = {"messages": [HumanMessage(content="Hi")], "agent_config": {"system_prompt": "You are helpful.", "model": "gpt-4o"}, "user_context": {}, "pending_ui": None, "tool_calls": None}
    result = await chat(state)
    assert "messages" in result

@pytest.mark.asyncio
async def test_tool_node_executes():
    mock_tools = AsyncMock()
    mock_tools.execute.return_value = ToolResult(tool_name="test", result="ok")
    node = make_tool_node(mock_tools)
    # ... test with tool_calls in state

@pytest.mark.asyncio
async def test_ui_push_node_validates():
    mock_validator = AsyncMock()
    mock_validator.validate_component.return_value = True
    node = make_ui_push_node(mock_validator)
    # ... test with push_ui tool call
```

**Step 2: Implement chat_node.py**

```python
from __future__ import annotations
from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

def make_chat_node(llm: BaseChatModel):
    async def chat_node(state: dict) -> dict:
        config = state["agent_config"]
        system = SystemMessage(content=config["system_prompt"])
        messages = [system] + state["messages"]
        response = await llm.ainvoke(messages)
        return {"messages": [response]}
    return chat_node
```

**Step 3: Implement tool_node.py**

```python
from __future__ import annotations
from langchain_core.messages import ToolMessage
from src.domain.ports.tools import ToolsPort

def make_tool_node(tools_port: ToolsPort):
    async def tool_node(state: dict) -> dict:
        last_message = state["messages"][-1]
        results = []
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "push_ui":
                continue  # handled by ui_push_node
            result = await tools_port.execute(tool_call["name"], tool_call["args"])
            results.append(ToolMessage(
                content=result.result,
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            ))
        return {"messages": results}
    return tool_node
```

**Step 4: Implement ui_push_node.py**

```python
from __future__ import annotations
from langchain_core.messages import ToolMessage
from src.domain.services.contract_validator import ContractValidator

def make_ui_push_node(validator: ContractValidator):
    async def ui_push_node(state: dict) -> dict:
        last_message = state["messages"][-1]
        pending_ui = []
        tool_messages = []
        for tool_call in last_message.tool_calls:
            if tool_call["name"] != "push_ui":
                continue
            payload = tool_call["args"]
            validator.validate_component(payload)
            pending_ui.append(payload)
            tool_messages.append(ToolMessage(
                content=f"UI component '{payload['type']}' pushed to user.",
                tool_call_id=tool_call["id"],
                name="push_ui",
            ))
        return {"messages": tool_messages, "pending_ui": pending_ui}
    return ui_push_node
```

**Step 5: Run tests, commit**

```bash
git commit -m "feat(backend): add LangGraph nodes — chat, tool, ui_push"
```

---

### Task 9: Graph edges and builder

**Files:**
- Create: `packages/backend/src/graph/edges.py`
- Create: `packages/backend/src/graph/builder.py`
- Test: `packages/backend/tests/unit/graph/test_edges.py`
- Test: `packages/backend/tests/unit/graph/test_builder.py`

**Step 1: Write failing tests for edges**

```python
# tests/unit/graph/test_edges.py
from langchain_core.messages import AIMessage
from src.graph.edges import route_after_llm

def test_route_to_end_when_no_tool_calls():
    state = {"messages": [AIMessage(content="Done")]}
    assert route_after_llm(state) == "__end__"

def test_route_to_tool_when_tool_calls():
    msg = AIMessage(content="", tool_calls=[{"name": "search", "args": {}, "id": "1"}])
    state = {"messages": [msg]}
    assert route_after_llm(state) == "tool_node"

def test_route_to_ui_push_when_push_ui():
    msg = AIMessage(content="", tool_calls=[{"name": "push_ui", "args": {"type": "form"}, "id": "1"}])
    state = {"messages": [msg]}
    assert route_after_llm(state) == "ui_push_node"
```

**Step 2: Implement edges.py**

```python
from langgraph.graph import END

def route_after_llm(state: dict) -> str:
    last = state["messages"][-1]
    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return END
    has_ui = any(tc["name"] == "push_ui" for tc in last.tool_calls)
    has_tools = any(tc["name"] != "push_ui" for tc in last.tool_calls)
    if has_ui:
        return "ui_push_node"
    if has_tools:
        return "tool_node"
    return END
```

**Step 3: Implement builder.py**

```python
from __future__ import annotations
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes.chat_node import make_chat_node
from src.graph.nodes.tool_node import make_tool_node
from src.graph.nodes.ui_push_node import make_ui_push_node
from src.graph.edges import route_after_llm
from src.domain.ports.tools import ToolsPort
from src.domain.services.contract_validator import ContractValidator

def build_graph(
    llm: BaseChatModel,
    tools_port: ToolsPort,
    validator: ContractValidator,
) -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("chat_node", make_chat_node(llm))
    graph.add_node("tool_node", make_tool_node(tools_port))
    graph.add_node("ui_push_node", make_ui_push_node(validator))

    graph.set_entry_point("chat_node")

    graph.add_conditional_edges("chat_node", route_after_llm, {
        "tool_node": "tool_node",
        "ui_push_node": "ui_push_node",
        END: END,
    })
    graph.add_edge("tool_node", "chat_node")
    graph.add_edge("ui_push_node", "chat_node")

    return graph.compile()
```

**Step 4: Run tests, commit**

```bash
git commit -m "feat(backend): add graph edges routing and builder"
```

---

## Phase 4: Backend Adapters

### Task 10: In-memory persistence adapter

**Files:**
- Create: `packages/backend/src/adapters/__init__.py`
- Create: `packages/backend/src/adapters/persistence/__init__.py`
- Create: `packages/backend/src/adapters/persistence/memory_adapter.py`
- Test: `packages/backend/tests/unit/adapters/test_memory_adapter.py`

**Step 1: Write failing tests**

```python
@pytest.mark.asyncio
async def test_save_and_load_conversation():
    adapter = InMemoryPersistenceAdapter()
    conv = Conversation(agent_id="test")
    await adapter.save_conversation(conv)
    loaded = await adapter.load_conversation(conv.id)
    assert loaded is not None
    assert loaded.id == conv.id

@pytest.mark.asyncio
async def test_delete_conversation():
    adapter = InMemoryPersistenceAdapter()
    conv = Conversation(agent_id="test")
    await adapter.save_conversation(conv)
    assert await adapter.delete_conversation(conv.id) is True
    assert await adapter.load_conversation(conv.id) is None
```

**Step 2: Implement InMemoryPersistenceAdapter**

Simple dict-based storage implementing `PersistencePort`.

**Step 3: Run tests, commit**

```bash
git commit -m "feat(backend): add in-memory persistence adapter"
```

---

### Task 11: JWT auth adapter

**Files:**
- Create: `packages/backend/src/adapters/auth/__init__.py`
- Create: `packages/backend/src/adapters/auth/jwt_adapter.py`
- Test: `packages/backend/tests/unit/adapters/test_jwt_adapter.py`

**Step 1: Write failing tests**

```python
@pytest.mark.asyncio
async def test_valid_token():
    adapter = JWTAuthAdapter(secret="test-secret", algorithm="HS256")
    token = jwt.encode({"sub": "user1", "tenant_id": "t1"}, "test-secret", algorithm="HS256")
    ctx = await adapter.validate_token(token)
    assert ctx is not None
    assert ctx.user_id == "user1"

@pytest.mark.asyncio
async def test_invalid_token():
    adapter = JWTAuthAdapter(secret="test-secret", algorithm="HS256")
    ctx = await adapter.validate_token("invalid")
    assert ctx is None
```

**Step 2: Implement JWTAuthAdapter**

Decode JWT with PyJWT, extract `sub` → `user_id`, `tenant_id`, `roles`.

**Step 3: Run tests, commit**

```bash
git commit -m "feat(backend): add JWT auth adapter"
```

---

### Task 12: LangChain LLM adapter

**Files:**
- Create: `packages/backend/src/adapters/llm/__init__.py`
- Create: `packages/backend/src/adapters/llm/langchain_adapter.py`

**Step 1: Implement LangChainLLMAdapter**

Thin wrapper around `ChatOpenAI` (or other LangChain chat models) that conforms to `LLMPort`. This adapter is primarily used by the graph builder directly via LangChain's `BaseChatModel`, so it's mostly configuration code.

```python
from langchain_openai import ChatOpenAI

def create_llm(provider: str, model: str, temperature: float, **kwargs) -> BaseChatModel:
    if provider == "openai":
        return ChatOpenAI(model=model, temperature=temperature, **kwargs)
    raise ValueError(f"Unknown LLM provider: {provider}")
```

**Step 2: Commit**

```bash
git commit -m "feat(backend): add LangChain LLM adapter factory"
```

---

### Task 13: MCP tools adapter

**Files:**
- Create: `packages/backend/src/adapters/tools/__init__.py`
- Create: `packages/backend/src/adapters/tools/mcp_adapter.py`

**Step 1: Implement MCPToolsAdapter**

```python
from __future__ import annotations
import yaml
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.domain.ports.tools import ToolsPort, ToolDefinition, ToolResult


class MCPToolsAdapter:
    """Connects to MCP servers defined in config, discovers and executes tools."""

    def __init__(self, config_path: str | Path) -> None:
        self._config_path = Path(config_path)
        self._sessions: dict[str, ClientSession] = {}
        self._tool_map: dict[str, str] = {}  # tool_name -> server_name

    async def initialize(self) -> None:
        config = yaml.safe_load(self._config_path.read_text())
        for server in config.get("servers", []):
            # Connect to each MCP server
            ...

    async def discover(self) -> list[ToolDefinition]:
        tools = []
        for name, session in self._sessions.items():
            server_tools = await session.list_tools()
            for tool in server_tools.tools:
                tools.append(ToolDefinition(
                    name=tool.name,
                    description=tool.description or "",
                    parameters=tool.inputSchema or {},
                ))
                self._tool_map[tool.name] = name
        return tools

    async def execute(self, tool_name: str, arguments: dict) -> ToolResult:
        server_name = self._tool_map.get(tool_name)
        if not server_name:
            return ToolResult(tool_name=tool_name, result=f"Unknown tool: {tool_name}", is_error=True)
        session = self._sessions[server_name]
        result = await session.call_tool(tool_name, arguments=arguments)
        return ToolResult(tool_name=tool_name, result=str(result.content))
```

**Step 2: Create config/mcp_servers.yaml**

```yaml
# MCP Server Configuration
# Add your MCP servers here
servers: []
#  - name: "example"
#    command: "npx"
#    args: ["-y", "@example/mcp-server"]
#    env: {}
```

**Step 3: Commit**

```bash
git commit -m "feat(backend): add MCP tools adapter with config-based discovery"
```

---

## Phase 5: Backend API Layer

### Task 14: FastAPI app, dependencies, health route

**Files:**
- Create: `packages/backend/src/api/__init__.py`
- Create: `packages/backend/src/api/app.py`
- Create: `packages/backend/src/api/dependencies.py`
- Create: `packages/backend/src/api/routes/__init__.py`
- Create: `packages/backend/src/api/routes/health.py`
- Create: `packages/backend/src/api/middleware/__init__.py`
- Create: `packages/backend/src/api/middleware/auth_middleware.py`
- Test: `packages/backend/tests/unit/api/test_health.py`

**Step 1: Write failing test**

```python
from fastapi.testclient import TestClient
from src.api.app import create_app

def test_health():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
```

**Step 2: Implement app factory, dependencies injection, health route, auth middleware**

- `app.py`: FastAPI factory that wires routes, CORS, middleware
- `dependencies.py`: reads env vars, instantiates adapters, provides them via `Depends()`
- `health.py`: simple `GET /api/health` → `{"status": "ok"}`
- `auth_middleware.py`: extracts Bearer token, calls `AuthPort.validate_token()`, sets `request.state.user`

**Step 3: Run tests, commit**

```bash
git commit -m "feat(backend): add FastAPI app factory with health route and auth middleware"
```

---

### Task 15: Conversation and chat routes

**Files:**
- Create: `packages/backend/src/api/routes/conversations.py`
- Create: `packages/backend/src/api/routes/chat.py`
- Create: `packages/backend/src/domain/services/agent_service.py`
- Test: `packages/backend/tests/unit/api/test_conversations.py`
- Test: `packages/backend/tests/unit/api/test_chat.py`

**Step 1: Write failing tests for conversations CRUD**

```python
def test_create_conversation():
    resp = client.post("/api/conversations", json={"agent_id": "default"}, headers=auth_headers)
    assert resp.status_code == 201
    assert "id" in resp.json()

def test_get_conversation():
    # create then get
    ...

def test_delete_conversation():
    # create then delete
    ...
```

**Step 2: Write failing tests for chat**

```python
def test_send_message():
    # create conversation, then send message
    resp = client.post(f"/api/conversations/{conv_id}/messages",
        json={"type": "text", "text": "Hello"},
        headers=auth_headers)
    assert resp.status_code == 201
```

**Step 3: Implement agent_service.py**

Orchestrates: receives user message → loads conversation → runs graph → streams events.

```python
class AgentService:
    def __init__(self, persistence: PersistencePort, graph, validator: ContractValidator):
        self._persistence = persistence
        self._graph = graph
        self._validator = validator

    async def handle_message(self, conversation_id: str, user_input: dict, user_context: dict):
        conversation = await self._persistence.load_conversation(conversation_id)
        # Build state, invoke graph, yield SSE events
        ...
```

**Step 4: Implement conversation routes (CRUD) and chat route (POST message + GET stream SSE)**

- `POST /api/conversations/{id}/messages` — accepts `user-response.schema.json`, invokes agent
- `GET /api/conversations/{id}/stream` — SSE endpoint using `sse-starlette`

**Step 5: Run tests, commit**

```bash
git commit -m "feat(backend): add conversation CRUD and chat routes with SSE streaming"
```

---

### Task 16: Agent config loader

**Files:**
- Create: `packages/backend/config/agents/default.yaml`
- Create: `packages/backend/src/domain/services/config_loader.py`
- Test: `packages/backend/tests/unit/domain/test_config_loader.py`

**Step 1: Create default.yaml**

```yaml
name: "default-assistant"
model: "gpt-4o"
system_prompt: |
  You are a helpful AI assistant. You can respond with text or push
  interactive UI components when appropriate.

  Available UI components: form, choice-list, confirmation, card-list.

  To push a UI component, use the push_ui tool with the JSON payload.

allowed_tools:
  - "*"

allowed_ui_components:
  - "form"
  - "choice-list"
  - "confirmation"
  - "card-list"
  - "message"

max_turns: 20
temperature: 0.7
```

**Step 2: Implement config_loader.py**

```python
import yaml
from pathlib import Path
from src.domain.models.agent_config import AgentConfig

def load_agent_config(config_path: str | Path) -> AgentConfig:
    data = yaml.safe_load(Path(config_path).read_text())
    return AgentConfig(**data)
```

**Step 3: Run tests, commit**

```bash
git commit -m "feat(backend): add agent config loader with default YAML config"
```

---

## Phase 6: Frontend MFE

### Task 17: Frontend project scaffolding

**Files:**
- Create: `packages/frontend/package.json`
- Create: `packages/frontend/tsconfig.json`
- Create: `packages/frontend/vite.config.ts`
- Create: `packages/frontend/index.html`
- Create: `packages/frontend/src/types/contracts.ts`

**Step 1: Init project with Lit + Vite + TypeScript**

`package.json` with dependencies: `lit`, `vite`, `typescript`.

`vite.config.ts` configured to build as library (Web Component output).

`tsconfig.json` with strict mode, ESNext target.

**Step 2: Create contracts.ts — TypeScript types mirroring JSON schemas**

```typescript
// Types generated from @agent-base/contracts
export type ComponentType = 'message' | 'form' | 'choice-list' | 'confirmation' | 'card-list';

export interface MessageComponent { type: 'message'; content: string; metadata?: Record<string, unknown>; }
export interface FormField { name: string; fieldType: string; label: string; placeholder?: string; required?: boolean; options?: { label: string; value: string }[]; validation?: Record<string, unknown>; defaultValue?: unknown; }
export interface FormComponent { type: 'form'; title: string; description?: string; fields: FormField[]; submitLabel?: string; cancelLabel?: string; }
export interface ChoiceItem { id: string; label: string; description?: string; icon?: string; }
export interface ChoiceListComponent { type: 'choice-list'; title: string; description?: string; multiple?: boolean; choices: ChoiceItem[]; }
export interface ConfirmationComponent { type: 'confirmation'; title: string; message: string; confirmLabel?: string; cancelLabel?: string; destructive?: boolean; }
export interface CardAction { label: string; actionId: string; }
export interface Card { id: string; title: string; subtitle?: string; body?: string; actions?: CardAction[]; }
export interface CardListComponent { type: 'card-list'; title?: string; cards: Card[]; }

export type UIComponent = MessageComponent | FormComponent | ChoiceListComponent | ConfirmationComponent | CardListComponent;

export type AgentEventType = 'token' | 'component' | 'tool_start' | 'tool_end' | 'error' | 'done';
export interface AgentEvent { eventType: AgentEventType; conversationId: string; timestamp: string; token?: string; component?: UIComponent; toolName?: string; error?: string; }

export type UserResponseType = 'text' | 'form_submit' | 'choice_select' | 'confirmation' | 'card_action';
export interface UserResponse { conversationId: string; type: UserResponseType; text?: string; formData?: Record<string, unknown>; selectedChoices?: string[]; confirmed?: boolean; cardActionId?: string; cardId?: string; }
```

**Step 3: Commit**

```bash
git commit -m "feat(frontend): scaffold Vite + Lit + TypeScript project with contract types"
```

---

### Task 18: API client & SSE event parser

**Files:**
- Create: `packages/frontend/src/services/api-client.ts`
- Create: `packages/frontend/src/services/event-parser.ts`

**Step 1: Implement api-client.ts**

```typescript
import type { UserResponse, AgentEvent } from '../types/contracts';

export class AgentAPIClient {
  constructor(private baseUrl: string, private token: string) {}

  async createConversation(agentId: string): Promise<{ id: string }> {
    const resp = await fetch(`${this.baseUrl}/api/conversations`, {
      method: 'POST',
      headers: this._headers(),
      body: JSON.stringify({ agent_id: agentId }),
    });
    return resp.json();
  }

  async sendMessage(conversationId: string, message: UserResponse): Promise<void> {
    await fetch(`${this.baseUrl}/api/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: this._headers(),
      body: JSON.stringify(message),
    });
  }

  streamEvents(conversationId: string, onEvent: (event: AgentEvent) => void): EventSource {
    const url = `${this.baseUrl}/api/conversations/${conversationId}/stream`;
    const es = new EventSource(url);
    es.onmessage = (e) => { onEvent(JSON.parse(e.data)); };
    return es;
  }

  private _headers() {
    return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` };
  }
}
```

**Step 2: Implement event-parser.ts**

Simple utility to parse SSE event data into typed `AgentEvent` objects.

**Step 3: Commit**

```bash
git commit -m "feat(frontend): add API client with SSE streaming support"
```

---

### Task 19: UI components — message, form, choice-list, confirmation, card-list

**Files:**
- Create: `packages/frontend/src/components/chat-message.ts`
- Create: `packages/frontend/src/components/chat-form.ts`
- Create: `packages/frontend/src/components/chat-choice-list.ts`
- Create: `packages/frontend/src/components/chat-confirmation.ts`
- Create: `packages/frontend/src/components/chat-card-list.ts`
- Create: `packages/frontend/src/components/component-registry.ts`

**Step 1: Implement each Lit component**

Each component:
- Extends `LitElement`
- Accepts its contract type as a property
- Renders the appropriate UI
- Dispatches a `user-response` CustomEvent when the user interacts

Example for `chat-form.ts`:

```typescript
@customElement('chat-form')
export class ChatForm extends LitElement {
  @property({ type: Object }) data!: FormComponent;

  private _handleSubmit(e: Event) {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const data = Object.fromEntries(formData.entries());
    this.dispatchEvent(new CustomEvent('user-response', {
      detail: { type: 'form_submit', formData: data },
      bubbles: true, composed: true,
    }));
  }

  render() {
    return html`
      <div class="form-container">
        <h3>${this.data.title}</h3>
        ${this.data.description ? html`<p>${this.data.description}</p>` : ''}
        <form @submit=${this._handleSubmit}>
          ${this.data.fields.map(field => this._renderField(field))}
          <button type="submit">${this.data.submitLabel ?? 'Submit'}</button>
        </form>
      </div>
    `;
  }
  // _renderField switches on fieldType...
}
```

**Step 2: Implement component-registry.ts**

```typescript
import { LitElement } from 'lit';
import { ChatMessage } from './chat-message';
import { ChatForm } from './chat-form';
import { ChatChoiceList } from './chat-choice-list';
import { ChatConfirmation } from './chat-confirmation';
import { ChatCardList } from './chat-card-list';

const registry = new Map<string, typeof LitElement>();
registry.set('message', ChatMessage as unknown as typeof LitElement);
registry.set('form', ChatForm as unknown as typeof LitElement);
registry.set('choice-list', ChatChoiceList as unknown as typeof LitElement);
registry.set('confirmation', ChatConfirmation as unknown as typeof LitElement);
registry.set('card-list', ChatCardList as unknown as typeof LitElement);

export function getComponent(type: string): typeof LitElement | undefined {
  return registry.get(type);
}

export function registerComponent(type: string, component: typeof LitElement): void {
  registry.set(type, component);
}
```

**Step 3: Commit**

```bash
git commit -m "feat(frontend): add all UI components and component registry"
```

---

### Task 20: Main `<agent-chat>` Web Component

**Files:**
- Create: `packages/frontend/src/agent-chat.ts`
- Create: `packages/frontend/src/styles/tokens.css`
- Create: `packages/frontend/src/styles/base.css`

**Step 1: Implement agent-chat.ts**

Main orchestrator component:
- Attributes: `api-url`, `token`, `agent-id`, `theme`, `lang`, `conversation-id`
- On connect: creates conversation (or loads existing), opens SSE stream
- Renders chat message list + input area
- Dispatches `agent-ready`, `agent-response`, `user-submitted`, `agent-error` events
- Uses component registry to dynamically render UI components pushed by agent

**Step 2: Implement CSS tokens and base styles**

Design tokens as CSS custom properties, theming support.

**Step 3: Update index.html for dev/demo page**

```html
<!DOCTYPE html>
<html>
<head><title>Agent Chat Demo</title></head>
<body>
  <agent-chat
    api-url="http://localhost:8000"
    token="dev-token"
    agent-id="default-assistant"
    theme="light"
  ></agent-chat>
  <script type="module" src="/src/agent-chat.ts"></script>
</body>
</html>
```

**Step 4: Commit**

```bash
git commit -m "feat(frontend): add main <agent-chat> Web Component with theming"
```

---

## Phase 7: Integration & Polish

### Task 21: PostgreSQL persistence adapter + Alembic migrations

**Files:**
- Create: `packages/backend/src/adapters/persistence/postgres_adapter.py`
- Create: `packages/backend/alembic.ini`
- Create: `packages/backend/alembic/env.py`
- Create: `packages/backend/alembic/versions/001_initial.py`

**Step 1: Implement PostgresAdapter**

SQLAlchemy async tables for conversations, messages, graph_state. Implements `PersistencePort`.

**Step 2: Create Alembic migration for initial schema**

Tables: `conversations`, `messages`, `graph_state`.

**Step 3: Commit**

```bash
git commit -m "feat(backend): add PostgreSQL persistence adapter with Alembic migrations"
```

---

### Task 22: End-to-end integration test

**Files:**
- Create: `packages/backend/tests/integration/test_full_flow.py`

**Step 1: Write integration test**

Uses in-memory adapter + mocked LLM. Tests the full flow:
1. Create conversation
2. Send text message
3. Agent responds with a form component
4. User submits form
5. Agent responds with confirmation

**Step 2: Run test, commit**

```bash
git commit -m "test(backend): add end-to-end integration test for full agent flow"
```

---

### Task 23: Vite library build for MFE distribution

**Files:**
- Modify: `packages/frontend/vite.config.ts`
- Modify: `packages/frontend/package.json`

**Step 1: Configure Vite lib mode**

Build as `agent-chat.js` single bundle, Web Component ready.

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    lib: {
      entry: 'src/agent-chat.ts',
      formats: ['es'],
      fileName: 'agent-chat',
    },
  },
});
```

**Step 2: Verify build**

Run: `cd packages/frontend && npm run build`
Expected: `dist/agent-chat.js` exists

**Step 3: Commit**

```bash
git commit -m "chore(frontend): configure Vite library build for MFE distribution"
```

---

### Task 24: Final docker-compose verification

**Step 1: Verify docker-compose builds**

Run: `docker-compose build`
Expected: all 3 services build without errors

**Step 2: Verify docker-compose up**

Run: `docker-compose up -d && curl http://localhost:8000/api/health`
Expected: `{"status": "ok"}`

**Step 3: Commit any fixes**

```bash
git commit -m "chore: finalize docker-compose and verify full stack boots"
```

---

## Summary

| Phase | Tasks | Description |
|---|---|---|
| 1 | 1-2 | Monorepo scaffolding + contracts schemas |
| 2 | 3-6 | Backend domain (models, ports, validator) |
| 3 | 7-9 | LangGraph agent graph (state, nodes, edges, builder) |
| 4 | 10-13 | Backend adapters (memory, JWT, LLM, MCP) |
| 5 | 14-16 | Backend API (FastAPI, routes, config) |
| 6 | 17-20 | Frontend MFE (Lit components, API client, main component) |
| 7 | 21-24 | Integration (Postgres, e2e tests, build, Docker) |

**Total: 24 tasks across 7 phases.**

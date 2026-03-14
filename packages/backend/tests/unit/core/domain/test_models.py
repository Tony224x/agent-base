from src.core.domain.entities.conversation import Conversation, Message, Role, UIComponentPayload
from src.core.domain.entities.agent_config import AgentConfig


def test_message_creation():
    msg = Message(role=Role.USER, content="hello")
    assert msg.role == Role.USER
    assert msg.content == "hello"
    assert msg.id is not None
    assert msg.timestamp is not None


def test_message_with_tool_calls():
    msg = Message(
        role=Role.ASSISTANT,
        content="",
        tool_calls=[{"name": "search", "args": {"q": "test"}, "id": "tc1"}],
    )
    assert msg.tool_calls is not None
    assert len(msg.tool_calls) == 1


def test_conversation_creation():
    conv = Conversation(agent_id="default")
    assert conv.agent_id == "default"
    assert conv.id is not None
    assert conv.messages == []


def test_conversation_add_message():
    conv = Conversation(agent_id="default")
    conv.add_message(Message(role=Role.USER, content="hi"))
    conv.add_message(Message(role=Role.ASSISTANT, content="hello"))
    assert len(conv.messages) == 2
    assert conv.messages[0].role == Role.USER
    assert conv.messages[1].role == Role.ASSISTANT


def test_ui_component_payload():
    payload = UIComponentPayload(
        component_type="form",
        data={"title": "Test", "fields": []},
    )
    assert payload.component_type == "form"
    assert payload.data["title"] == "Test"


def test_agent_config_allows_tool_wildcard():
    config = AgentConfig(
        name="test",
        model="gpt-4o",
        system_prompt="Test",
        allowed_tools=["*"],
    )
    assert config.allows_tool("anything") is True


def test_agent_config_allows_tool_specific():
    config = AgentConfig(
        name="test",
        model="gpt-4o",
        system_prompt="Test",
        allowed_tools=["search", "calculator"],
    )
    assert config.allows_tool("search") is True
    assert config.allows_tool("delete") is False


def test_agent_config_allows_ui_component():
    config = AgentConfig(
        name="test",
        model="gpt-4o",
        system_prompt="Test",
        allowed_ui_components=["form", "message"],
    )
    assert config.allows_ui_component("form") is True
    assert config.allows_ui_component("unknown") is False

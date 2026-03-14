import pytest
from pathlib import Path

from src.domain.services.contract_validator import ContractValidator

CONTRACTS_DIR = Path(__file__).resolve().parents[4] / "contracts"


@pytest.fixture
def validator():
    return ContractValidator(schemas_dir=CONTRACTS_DIR)


def test_loads_all_component_types(validator):
    types = validator.get_known_types()
    assert "message" in types
    assert "form" in types
    assert "choice-list" in types
    assert "confirmation" in types
    assert "card-list" in types


def test_validate_message_component(validator):
    payload = {"type": "message", "content": "Hello world"}
    assert validator.validate_component(payload) is True


def test_validate_form_component(validator):
    payload = {
        "type": "form",
        "title": "Test Form",
        "fields": [
            {"name": "email", "fieldType": "email", "label": "Email"},
            {
                "name": "priority",
                "fieldType": "select",
                "label": "Priority",
                "options": [
                    {"label": "Low", "value": "low"},
                    {"label": "High", "value": "high"},
                ],
            },
        ],
        "submitLabel": "Send",
    }
    assert validator.validate_component(payload) is True


def test_validate_choice_list_component(validator):
    payload = {
        "type": "choice-list",
        "title": "Pick one",
        "choices": [
            {"id": "a", "label": "Option A"},
            {"id": "b", "label": "Option B", "description": "The second option"},
        ],
    }
    assert validator.validate_component(payload) is True


def test_validate_confirmation_component(validator):
    payload = {
        "type": "confirmation",
        "title": "Delete item?",
        "message": "This action cannot be undone.",
        "destructive": True,
    }
    assert validator.validate_component(payload) is True


def test_validate_card_list_component(validator):
    payload = {
        "type": "card-list",
        "title": "Results",
        "cards": [
            {
                "id": "1",
                "title": "Result 1",
                "body": "Description",
                "actions": [{"label": "View", "actionId": "view_1"}],
            },
        ],
    }
    assert validator.validate_component(payload) is True


def test_reject_invalid_form_missing_fields(validator):
    payload = {"type": "form", "title": "Incomplete"}
    with pytest.raises(ValueError, match="Invalid form component"):
        validator.validate_component(payload)


def test_reject_unknown_type(validator):
    payload = {"type": "unknown_widget", "data": {}}
    with pytest.raises(ValueError, match="Unknown component type"):
        validator.validate_component(payload)


def test_reject_message_missing_content(validator):
    payload = {"type": "message"}
    with pytest.raises(ValueError, match="Invalid message component"):
        validator.validate_component(payload)

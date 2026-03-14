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

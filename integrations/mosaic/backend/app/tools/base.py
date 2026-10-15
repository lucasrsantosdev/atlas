from abc import ABC, abstractmethod
import math
from pathlib import Path
from typing import Any, Callable


class Tool(ABC):
    name: str
    description: str
    input_schema: dict[str, Any]
    permission_policy: dict[str, Any]

    @abstractmethod
    def execute(
        self,
        arguments: dict[str, Any],
        *,
        workspace: Path | None = None,
        cancel_check: Callable[[], bool] | None = None,
    ) -> Any:
        raise NotImplementedError

    def validate(self, arguments: dict[str, Any]) -> None:
        """Validate the supported JSON-schema subset and reject unknown input."""
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")
        if any(not isinstance(key, str) for key in arguments):
            raise ValueError("Tool argument names must be strings")

        schema = self.input_schema
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if schema.get("additionalProperties", False) is not True:
            unknown = set(arguments) - set(properties)
            if unknown:
                raise ValueError(f"Unknown argument(s): {', '.join(sorted(unknown))}")

        missing = [field for field in required if field not in arguments]
        if missing:
            raise ValueError(f"Missing required argument(s): {', '.join(missing)}")

        max_properties = schema.get("maxProperties")
        if max_properties is not None and len(arguments) > max_properties:
            raise ValueError("Too many tool arguments")

        for field, value in arguments.items():
            field_schema = properties.get(field)
            if field_schema is None:
                if schema.get("additionalProperties", False) is not True:
                    raise ValueError(f"Unknown argument: {field}")
                continue

            expected_type = field_schema.get("type")
            type_valid = {
                "string": lambda v: isinstance(v, str),
                "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and (isinstance(v, int) or math.isfinite(v)),
                "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
                "boolean": lambda v: isinstance(v, bool),
                "object": lambda v: isinstance(v, dict),
                "array": lambda v: isinstance(v, list),
                "null": lambda v: v is None,
            }.get(expected_type)
            if type_valid is None:
                raise ValueError(f"Unsupported schema type for {field}: {expected_type}")
            if not type_valid(value):
                raise ValueError(f"Argument {field} must be {expected_type}")

            if "enum" in field_schema and value not in field_schema["enum"]:
                raise ValueError(f"Argument {field} must be one of: {', '.join(map(str, field_schema['enum']))}")

            if isinstance(value, str):
                if len(value) < field_schema.get("minLength", 0):
                    raise ValueError(f"Argument {field} is too short")
                if len(value) > field_schema.get("maxLength", 100_000):
                    raise ValueError(f"Argument {field} exceeds the maximum length")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if value < field_schema.get("minimum", float("-inf")):
                    raise ValueError(f"Argument {field} is below the minimum")
                if value > field_schema.get("maximum", float("inf")):
                    raise ValueError(f"Argument {field} exceeds the maximum")
            if isinstance(value, list) and len(value) > field_schema.get("maxItems", 1000):
                raise ValueError(f"Argument {field} has too many items")
            if isinstance(value, dict) and len(value) > field_schema.get("maxProperties", 100):
                raise ValueError(f"Argument {field} has too many properties")

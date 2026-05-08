"""Validation for the normalized PolyTrack test-builder block schema."""

from __future__ import annotations

from typing import Any, Sequence

REQUIRED_VECTOR_LENGTH = 3
REQUIRED_FIELDS = {"id", "type", "position", "rotation", "scale"}


def validate_track(blocks: Sequence[dict[str, Any]]) -> str | None:
    """Return ``None`` for a valid track or a human-readable validation error."""

    if not blocks:
        return "Track must contain at least one block"

    seen_ids: set[int] = set()
    has_start = False
    has_finish = False

    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            return f"Block {index} must be an object"
        missing = REQUIRED_FIELDS.difference(block)
        if missing:
            return f"Block {index} is missing required fields: {', '.join(sorted(missing))}"
        if not isinstance(block["id"], int):
            return f"Block {index} id must be an integer"
        if block["id"] in seen_ids:
            return f"Duplicate block id: {block['id']}"
        seen_ids.add(block["id"])
        if not isinstance(block["type"], str) or not block["type"]:
            return f"Block {index} type must be a non-empty string"
        for field_name in ("position", "rotation", "scale"):
            value = block[field_name]
            if not isinstance(value, list) or len(value) != REQUIRED_VECTOR_LENGTH:
                return f"Block {index} {field_name} must be a 3-value list"
            if not all(isinstance(component, (int, float)) for component in value):
                return f"Block {index} {field_name} must contain only numbers"
        has_start = has_start or block["type"] == "start"
        has_finish = has_finish or block["type"] == "finish"

    if not has_start:
        return "Track must contain a start block"
    if not has_finish:
        return "Track must contain a finish block"

    return None

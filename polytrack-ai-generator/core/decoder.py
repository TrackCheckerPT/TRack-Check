"""PolyTrack export-code decoder."""

from __future__ import annotations

import base64
import json
from typing import Any

from core.encoder import EXPORT_PREFIX, FORMAT_NAME, FORMAT_VERSION
from utils.validator import validate_track


def import_polytrack(code: str) -> tuple[list[dict[str, Any]], str | None]:
    """Decode a PolyTrack1-prefixed export code.

    Returns ``(blocks, None)`` on success and ``([], error_message)`` on failure
    so command-line tools can report import problems without exception handling.
    """

    normalized = "".join(code.split())
    if not normalized.startswith(EXPORT_PREFIX):
        return [], f"Track code must start with {EXPORT_PREFIX}"

    payload = normalized[len(EXPORT_PREFIX) :]
    if not payload:
        return [], "Track code is missing an encoded payload"

    try:
        padded_payload = payload + "=" * (-len(payload) % 4)
        decoded_json = base64.urlsafe_b64decode(padded_payload.encode("ascii"))
        document = json.loads(decoded_json.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [], f"Track code payload could not be decoded: {exc}"

    if document.get("format") != FORMAT_NAME:
        return [], "Track code format is not supported by this test builder"
    if document.get("version") != FORMAT_VERSION:
        return [], f"Unsupported track code version: {document.get('version')!r}"

    blocks = document.get("blocks")
    if not isinstance(blocks, list):
        return [], "Track code payload must contain a block list"

    validation = validate_track(blocks)
    if validation:
        return [], validation

    return blocks, None

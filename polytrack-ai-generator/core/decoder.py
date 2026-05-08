"""PolyTrack 0.5.2 export-code decoder."""

from __future__ import annotations

import base64
import binascii
from typing import Any

import msgpack
import zstandard as zstd

from core.encoder import EXPORT_PREFIX, TRACK_VERSION
from utils.validator import validate_track


def import_polytrack(code: str) -> tuple[list[list[int | float]], str | None]:
    """Decode a PolyTrack1 export code into compact block arrays.

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
        compressed = base64.b64decode(payload.encode("utf-8"), validate=True)
        packed = zstd.decompress(compressed)
        document = msgpack.unpackb(packed, raw=False)
    except (
        ValueError,
        binascii.Error,
        msgpack.ExtraData,
        msgpack.FormatError,
        zstd.ZstdError,
        UnicodeDecodeError,
    ) as exc:
        return [], f"Track code payload could not be decoded: {exc}"

    package_error = _validate_package(document)
    if package_error is not None:
        return [], package_error

    blocks = document["b"]
    validation = validate_track(blocks)
    if validation:
        return [], validation

    return blocks, None


def _validate_package(document: Any) -> str | None:
    if not isinstance(document, dict):
        return "Track code payload must be a metadata object"
    if document.get("v") != TRACK_VERSION:
        return f"Unsupported track code version: {document.get('v')!r}"
    if not isinstance(document.get("a"), str) or not document["a"]:
        return "Track code payload must contain an author"
    if not isinstance(document.get("n"), str) or not document["n"]:
        return "Track code payload must contain a track name"
    if not isinstance(document.get("b"), list):
        return "Track code payload must contain a block list"
    return None

"""PolyTrack export-code encoder.

The official Kodub game currently uses the ``PolyTrack1`` code prefix.  This
module provides a deterministic, test-friendly encoder for the repository's
normalized block schema so generated tracks can be round-tripped and regression
checked while the project grows toward fuller editor compatibility.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Iterable, Mapping

EXPORT_PREFIX = "PolyTrack1"
FORMAT_NAME = "TRack-Check/PolyTrack1"
FORMAT_VERSION = 1


def export_polytrack(blocks: Iterable[Mapping[str, Any]]) -> str:
    """Encode normalized track blocks into a PolyTrack1-prefixed export code."""

    payload = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "blocks": list(blocks),
    }
    encoded_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    encoded_payload = base64.urlsafe_b64encode(encoded_json).decode("ascii")
    return f"{EXPORT_PREFIX}{encoded_payload.rstrip('=')}"

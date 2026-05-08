"""PolyTrack 0.5.2 export-code encoder.

PolyTrack 0.5.2 expects ``PolyTrack1`` codes to contain a Base64-encoded
Zstandard stream. The decompressed bytes are a MessagePack map with track
metadata and a compact block array list.
"""

from __future__ import annotations

import base64
from collections.abc import Iterable, Sequence

import msgpack
import zstandard as zstd

from utils.validator import validate_track

EXPORT_PREFIX = "PolyTrack1"
TRACK_VERSION = 2
DEFAULT_AUTHOR = "Zawg"
DEFAULT_TRACK_NAME = "AI_Wild_Build"
ZSTD_LEVEL = 3

Block = Sequence[int | float]


def export_polytrack(
    blocks: Iterable[Block],
    *,
    author: str = DEFAULT_AUTHOR,
    name: str = DEFAULT_TRACK_NAME,
) -> str:
    """Encode PolyTrack 0.5.2 blocks into a game-compatible export code."""

    block_list = [list(block) for block in blocks]
    validation = validate_track(block_list)
    if validation is not None:
        raise ValueError(validation)

    track_package = {
        "v": TRACK_VERSION,
        "a": author,
        "n": name,
        "b": block_list,
    }
    packed = msgpack.packb(track_package, use_bin_type=True)
    compressed = zstd.compress(packed, level=ZSTD_LEVEL)
    encoded_payload = base64.b64encode(compressed).decode("utf-8")
    return f"{EXPORT_PREFIX}{encoded_payload}"

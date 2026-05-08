"""Validation for PolyTrack 0.5.2 compact block arrays."""

from __future__ import annotations

from typing import Sequence

BLOCK_LENGTH = 5
BLOCK_TYPES = {
    0: "Road_Straight",
    1: "Road_Curve_90",
    5: "Start_Line",
    6: "Finish_Line",
    10: "Pillar_Square",
    12: "Road_Slope",
    22: "Checkpoint",
}
START_LINE = 5
FINISH_LINE = 6


def validate_track(blocks: Sequence[Sequence[int | float]]) -> str | None:
    """Return ``None`` for a valid track or a human-readable validation error."""

    if not blocks:
        return "Track must contain at least one block"

    start_count = 0
    finish_count = 0

    for index, block in enumerate(blocks):
        if not isinstance(block, list):
            return f"Block {index} must be a 5-value array"
        if len(block) != BLOCK_LENGTH:
            return f"Block {index} must contain [ID, X, Y, Z, Rotation]"

        block_id, x, y, z, rotation = block
        if not isinstance(block_id, int):
            return f"Block {index} id must be an integer"
        if block_id not in BLOCK_TYPES:
            return f"Block {index} has unsupported block id: {block_id}"
        if not all(isinstance(value, (int, float)) for value in (x, y, z, rotation)):
            return f"Block {index} coordinates and rotation must contain only numbers"

        start_count += block_id == START_LINE
        finish_count += block_id == FINISH_LINE

    if start_count != 1:
        return "Track must contain exactly one start line"
    if finish_count < 1:
        return "Track must contain at least one finish line"

    return None

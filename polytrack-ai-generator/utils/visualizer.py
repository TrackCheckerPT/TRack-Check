"""ASCII visualization helpers for generated track tests."""

from __future__ import annotations

from typing import Any, Sequence

_SYMBOLS = {
    "start": "S",
    "finish": "F",
    "road": "#",
    "checkpoint": "C",
    "barrier": "X",
    "boost": ">",
    "jump": "^",
}


def visualize_track_2d(blocks: Sequence[dict[str, Any]], plane: str = "xy") -> str:
    """Render a coarse top-down ASCII map for terminal smoke tests."""

    if plane != "xy":
        raise ValueError("Only xy visualization is currently supported")
    if not blocks:
        return ""

    points = [
        (round(block["position"][0]), round(block["position"][1]), block.get("type", "road"))
        for block in blocks
    ]
    min_x = min(x for x, _, _ in points)
    max_x = max(x for x, _, _ in points)
    min_y = min(y for _, y, _ in points)
    max_y = max(y for _, y, _ in points)

    width = max_x - min_x + 1
    height = max_y - min_y + 1
    canvas = [["." for _ in range(width)] for _ in range(height)]

    for x, y, block_type in points:
        canvas[max_y - y][x - min_x] = _SYMBOLS.get(block_type, "?")

    return "\n".join("".join(row) for row in canvas)

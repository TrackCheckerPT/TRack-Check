"""ASCII visualization helpers for generated PolyTrack block arrays."""

from __future__ import annotations

from typing import Sequence

_SYMBOLS = {
    0: "#",
    1: ")",
    5: "S",
    6: "F",
    10: "P",
    12: "/",
    22: "C",
}


def visualize_track_2d(blocks: Sequence[Sequence[int | float]], plane: str = "xz") -> str:
    """Render a coarse top-down ASCII map for terminal smoke tests."""

    if plane != "xz":
        raise ValueError("Only xz visualization is currently supported")
    if not blocks:
        return ""

    points = [(round(block[1]), round(block[3]), block[0]) for block in blocks]
    min_x = min(x for x, _, _ in points)
    max_x = max(x for x, _, _ in points)
    min_z = min(z for _, z, _ in points)
    max_z = max(z for _, z, _ in points)

    width = max_x - min_x + 1
    height = max_z - min_z + 1
    canvas = [["." for _ in range(width)] for _ in range(height)]

    for x, z, block_id in points:
        canvas[max_z - z][x - min_x] = _SYMBOLS.get(block_id, "?")

    return "\n".join("".join(row) for row in canvas)

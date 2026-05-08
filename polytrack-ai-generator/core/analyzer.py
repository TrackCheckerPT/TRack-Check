"""Small analysis utilities for generated test tracks."""

from __future__ import annotations

import math
from typing import Any, Sequence


class TrackAnalyzer:
    """Calculate simple metrics for normalized track block lists."""

    def __init__(self, blocks: Sequence[dict[str, Any]]) -> None:
        self.blocks = list(blocks)

    def estimate_length(self) -> float:
        """Estimate drivable length from ordered road/start/finish blocks."""

        drive_blocks = [
            block
            for block in self.blocks
            if block.get("type") in {"road", "start", "finish", "checkpoint"}
        ]
        distance = 0.0
        for previous, current in zip(drive_blocks, drive_blocks[1:]):
            px, py, pz = previous["position"]
            cx, cy, cz = current["position"]
            distance += math.dist((px, py, pz), (cx, cy, cz))
        return round(distance, 3)

    def get_difficulty(self) -> str:
        """Classify generated tracks using block count and obstacle density."""

        obstacle_count = sum(
            1 for block in self.blocks if block.get("type") in {"barrier", "boost", "jump"}
        )
        if obstacle_count >= 4 or len(self.blocks) >= 14:
            return "hard"
        if obstacle_count >= 2 or len(self.blocks) >= 10:
            return "medium"
        return "easy"

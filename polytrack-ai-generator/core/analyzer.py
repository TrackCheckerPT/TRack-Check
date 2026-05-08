"""Small analysis utilities for generated PolyTrack block arrays."""

from __future__ import annotations

import math
from typing import Sequence

DRIVABLE_BLOCK_IDS = {0, 1, 5, 6, 12, 22}
DIFFICULTY_BLOCK_IDS = {1, 10, 12, 22}


class TrackAnalyzer:
    """Calculate simple metrics for PolyTrack 0.5.2 block lists."""

    def __init__(self, blocks: Sequence[Sequence[int | float]]) -> None:
        self.blocks = list(blocks)

    def estimate_length(self) -> float:
        """Estimate drivable length from ordered road/start/finish/checkpoint blocks."""

        drive_blocks = [block for block in self.blocks if block[0] in DRIVABLE_BLOCK_IDS]
        distance = 0.0
        for previous, current in zip(drive_blocks, drive_blocks[1:]):
            px, py, pz = previous[1:4]
            cx, cy, cz = current[1:4]
            distance += math.dist((px, py, pz), (cx, cy, cz))
        return round(distance, 3)

    def get_difficulty(self) -> str:
        """Classify generated tracks using block count and technical block density."""

        technical_count = sum(1 for block in self.blocks if block[0] in DIFFICULTY_BLOCK_IDS)
        if technical_count >= 8 or len(self.blocks) >= 18:
            return "hard"
        if technical_count >= 4 or len(self.blocks) >= 10:
            return "medium"
        return "easy"

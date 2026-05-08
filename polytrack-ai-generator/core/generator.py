"""Deterministic helpers for building small PolyTrack-style test tracks."""

from __future__ import annotations

import random
from typing import Any

Block = dict[str, Any]


class TrackGenerator:
    """Generate predictable tracks for codec, analyzer, and visual tests."""

    def __init__(self, seed: int | None = None, segment_spacing: float = 8.0) -> None:
        self.random = random.Random(seed)
        self.segment_spacing = segment_spacing

    def _block(
        self,
        block_type: str,
        index: int,
        x: float,
        y: float,
        z: float = 0.0,
        rotation_y: float = 0.0,
    ) -> Block:
        return {
            "id": index,
            "type": block_type,
            "position": [round(x, 3), round(y, 3), round(z, 3)],
            "rotation": [0.0, round(rotation_y, 3), 0.0],
            "scale": [1.0, 1.0, 1.0],
        }

    def generate_simple_circuit(self, length: int = 8) -> list[Block]:
        """Create a rectangular loop with start and finish markers."""

        if length < 4:
            raise ValueError("A simple circuit needs at least 4 segments")

        blocks: list[Block] = []
        spacing = self.segment_spacing
        side_length = max(1, (length + 3) // 4)
        coordinates: list[tuple[float, float, float]] = []
        x = 0.0
        y = 0.0

        for dx, dy, rotation in (
            (spacing, 0.0, 0.0),
            (0.0, spacing, 90.0),
            (-spacing, 0.0, 180.0),
            (0.0, -spacing, 270.0),
        ):
            for _ in range(side_length):
                coordinates.append((x, y, rotation))
                x += dx
                y += dy

        for index, (x, y, rotation) in enumerate(coordinates[:length]):
            block_type = "road"
            if index == 0:
                block_type = "start"
            elif index == min(length - 1, len(coordinates) - 1):
                block_type = "finish"
            blocks.append(self._block(block_type, index, x, y, rotation_y=rotation))

        return blocks

    def generate_with_obstacles(
        self, length: int = 10, difficulty: str = "medium"
    ) -> list[Block]:
        """Create a straight test track and insert deterministic obstacles."""

        if length < 3:
            raise ValueError("An obstacle test track needs at least 3 segments")
        if difficulty not in {"easy", "medium", "hard"}:
            raise ValueError("difficulty must be one of: easy, medium, hard")

        blocks = [
            self._block(
                "start" if index == 0 else "finish" if index == length - 1 else "road",
                index,
                index * self.segment_spacing,
                0.0,
            )
            for index in range(length)
        ]

        obstacle_counts = {"easy": 1, "medium": 2, "hard": 4}
        candidate_indexes = list(range(1, length - 1))
        self.random.shuffle(candidate_indexes)
        for obstacle_number, segment_index in enumerate(
            sorted(candidate_indexes[: obstacle_counts[difficulty]]), start=1
        ):
            x, y, z = blocks[segment_index]["position"]
            blocks.append(
                self._block(
                    "barrier",
                    length + obstacle_number - 1,
                    x,
                    y + self.random.choice([-2.0, 2.0]),
                    z,
                )
            )

        return blocks


def generate_all_tests() -> dict[str, str]:
    """Generate representative tracks and return their export codes."""

    from core.analyzer import TrackAnalyzer
    from core.decoder import import_polytrack
    from core.encoder import export_polytrack
    from utils.visualizer import visualize_track_2d

    scenarios = {
        "SIMPLE_CIRCUIT": (
            TrackGenerator(seed=123),
            lambda generator: generator.generate_simple_circuit(length=8),
        ),
        "MEDIUM_RALLY": (
            TrackGenerator(seed=456),
            lambda generator: generator.generate_with_obstacles(
                length=10, difficulty="medium"
            ),
        ),
        "HARD_RALLY": (
            TrackGenerator(seed=789),
            lambda generator: generator.generate_with_obstacles(
                length=12, difficulty="hard"
            ),
        ),
    }

    codes: dict[str, str] = {}
    for name, (generator, build_track) in scenarios.items():
        blocks = build_track(generator)
        export_code = export_polytrack(blocks)
        decoded, error = import_polytrack(export_code)
        if error is not None:
            raise RuntimeError(f"{name} failed round-trip validation: {error}")

        analyzer = TrackAnalyzer(decoded)
        print(f"\n{name}")
        print(f"  blocks: {len(decoded)}")
        print(f"  difficulty: {analyzer.get_difficulty()}")
        print(f"  estimated length: {analyzer.estimate_length()} units")
        print(f"  export code: {export_code}")
        print(visualize_track_2d(decoded))
        codes[name] = export_code

    return codes


if __name__ == "__main__":
    generate_all_tests()

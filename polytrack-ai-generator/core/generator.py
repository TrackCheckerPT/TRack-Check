"""Deterministic helpers for building small PolyTrack-style test tracks."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any, Callable, Sequence

Block = dict[str, Any]
TrackBuilder = Callable[["TrackGenerator"], list[Block]]


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


def generate_track(
    track: str = "simple-circuit",
    *,
    length: int | None = None,
    difficulty: str = "medium",
    seed: int | None = 123,
    segment_spacing: float = 8.0,
) -> list[Block]:
    """Generate one named test track."""

    generator = TrackGenerator(seed=seed, segment_spacing=segment_spacing)
    if track == "simple-circuit":
        return generator.generate_simple_circuit(length=8 if length is None else length)
    if track == "obstacle":
        return generator.generate_with_obstacles(
            length=10 if length is None else length,
            difficulty=difficulty,
        )
    raise ValueError("track must be one of: simple-circuit, obstacle")


def generate_code(
    track: str = "simple-circuit",
    *,
    length: int | None = None,
    difficulty: str = "medium",
    seed: int | None = 123,
    segment_spacing: float = 8.0,
) -> str:
    """Generate one PolyTrack1 code string."""

    blocks = generate_track(
        track,
        length=length,
        difficulty=difficulty,
        seed=seed,
        segment_spacing=segment_spacing,
    )
    return _export_and_validate(blocks, track)


def generate_all_tests(*, verbose: bool = True) -> dict[str, str]:
    """Generate representative tracks and return export codes."""

    scenarios: dict[str, tuple[TrackGenerator, TrackBuilder]] = {
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
        code = _export_and_validate(blocks, name)
        if verbose:
            _print_summary(name, blocks, code)
        codes[name] = code

    return codes


def _export_and_validate(blocks: list[Block], name: str = "track") -> str:
    from core.decoder import import_polytrack
    from core.encoder import export_polytrack

    code = export_polytrack(blocks)
    decoded, error = import_polytrack(code)
    if error is not None:
        raise RuntimeError(f"{name} failed round-trip validation: {error}")
    if decoded != blocks:
        raise RuntimeError(f"{name} failed round-trip validation: decoded blocks differ")
    return code


def _print_summary(name: str, blocks: list[Block], code: str) -> None:
    from core.analyzer import TrackAnalyzer
    from utils.visualizer import visualize_track_2d

    analyzer = TrackAnalyzer(blocks)
    print(f"\n{name}")
    print(f"  blocks: {len(blocks)}")
    print(f"  difficulty: {analyzer.get_difficulty()}")
    print(f"  estimated length: {analyzer.estimate_length()} units")
    print(f"  export code: {code}")
    print(visualize_track_2d(blocks))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate deterministic PolyTrack1 test-builder codes."
    )
    parser.add_argument(
        "track",
        nargs="?",
        default="all",
        choices=("all", "simple-circuit", "obstacle"),
        help="Track preset to generate. Use 'all' for verbose sample output.",
    )
    parser.add_argument("--length", type=int, help="Number of road segments to build.")
    parser.add_argument(
        "--difficulty",
        choices=("easy", "medium", "hard"),
        default="medium",
        help="Obstacle density for the obstacle preset.",
    )
    parser.add_argument("--seed", type=int, default=123, help="Deterministic RNG seed.")
    parser.add_argument(
        "--segment-spacing",
        type=float,
        default=8.0,
        help="Distance between generated road segments.",
    )
    parser.add_argument(
        "--code-only",
        action="store_true",
        help="Print only PolyTrack1 code strings with no labels or previews.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file path for writing generated code strings.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line entrypoint for generating PolyTrack1 codes."""

    args = _build_parser().parse_args(argv)

    if args.track == "all":
        if args.code_only:
            codes = generate_all_tests(verbose=False)
            output = "\n".join(codes.values())
            print(output)
        else:
            codes = generate_all_tests()
            output = "\n".join(f"{name}: {code}" for name, code in codes.items())
    else:
        blocks = generate_track(
            args.track,
            length=args.length,
            difficulty=args.difficulty,
            seed=args.seed,
            segment_spacing=args.segment_spacing,
        )
        code = _export_and_validate(blocks, args.track)
        output = code
        if args.code_only:
            print(code)
        else:
            _print_summary(args.track.upper(), blocks, code)

    if args.output is not None:
        args.output.write_text(f"{output}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

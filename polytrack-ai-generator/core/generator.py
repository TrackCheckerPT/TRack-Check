"""Deterministic helpers for building PolyTrack 0.5.2 export tracks."""

from __future__ import annotations

import argparse
import random
from collections.abc import Callable, Sequence
from pathlib import Path

Block = list[int | float]
TrackBuilder = Callable[["TrackGenerator"], list[Block]]

ROAD_STRAIGHT = 0
ROAD_CURVE_90 = 1
START_LINE = 5
FINISH_LINE = 6
PILLAR_SQUARE = 10
ROAD_SLOPE = 12
CHECKPOINT = 22


class TrackGenerator:
    """Generate predictable tracks for codec, analyzer, and visual tests."""

    def __init__(self, seed: int | None = None, segment_spacing: float = 8.0) -> None:
        self.random = random.Random(seed)
        self.segment_spacing = segment_spacing

    def _block(
        self,
        block_id: int,
        x: float,
        y: float,
        z: float,
        rotation: float = 0.0,
    ) -> Block:
        return [
            block_id,
            round(x, 3),
            round(y, 3),
            round(z, 3),
            round(rotation, 3),
        ]

    def generate_simple_circuit(self, length: int = 8) -> list[Block]:
        """Create a rectangular loop with one start and at least one finish line."""

        if length < 4:
            raise ValueError("A simple circuit needs at least 4 segments")

        blocks: list[Block] = []
        spacing = self.segment_spacing
        side_length = max(1, (length + 3) // 4)
        coordinates: list[tuple[float, float, float, bool]] = []
        x = 0.0
        z = 0.0

        for dx, dz, rotation in (
            (spacing, 0.0, 0.0),
            (0.0, spacing, 90.0),
            (-spacing, 0.0, 180.0),
            (0.0, -spacing, 270.0),
        ):
            for step in range(side_length):
                coordinates.append((x, z, rotation, step == 0))
                x += dx
                z += dz

        for index, (x, z, rotation, starts_side) in enumerate(coordinates[:length]):
            block_id = (
                ROAD_CURVE_90
                if starts_side and index not in {0, length - 1}
                else ROAD_STRAIGHT
            )
            if index == 0:
                block_id = START_LINE
            elif index == length - 1:
                block_id = FINISH_LINE
            blocks.append(self._block(block_id, x, 0.0, z, rotation))

        return blocks

    def generate_with_obstacles(
        self, length: int = 10, difficulty: str = "medium"
    ) -> list[Block]:
        """Create a straight bridge with checkpoints and structural pillars."""

        if length < 3:
            raise ValueError("An obstacle test track needs at least 3 segments")
        if difficulty not in {"easy", "medium", "hard"}:
            raise ValueError("difficulty must be one of: easy, medium, hard")

        checkpoint_counts = {"easy": 0, "medium": 1, "hard": 2}
        pillar_counts = {"easy": 1, "medium": 3, "hard": 5}
        checkpoint_indexes = self._sample_indexes(length, checkpoint_counts[difficulty])

        blocks: list[Block] = []
        for index in range(length):
            if index == 0:
                block_id = START_LINE
            elif index == length - 1:
                block_id = FINISH_LINE
            elif index in checkpoint_indexes:
                block_id = CHECKPOINT
            else:
                block_id = ROAD_STRAIGHT
            blocks.append(self._block(block_id, 0.0, 0.0, index * self.segment_spacing))

        for segment_index in self._sample_indexes(length, pillar_counts[difficulty]):
            z = segment_index * self.segment_spacing
            blocks.append(self._block(PILLAR_SQUARE, -2.0, -4.0, z))
            blocks.append(self._block(PILLAR_SQUARE, 2.0, -4.0, z))

        return blocks

    def generate_wild_build(self, length: int = 18) -> list[Block]:
        """Create a larger decorative route with slopes, checkpoints, and pillars."""

        if length < 8:
            raise ValueError("A wild build needs at least 8 segments")

        blocks: list[Block] = []
        x = 0.0
        y = 0.0
        z = 0.0
        rotation = 0.0
        directions = {
            0.0: (0.0, self.segment_spacing),
            90.0: (self.segment_spacing, 0.0),
            180.0: (0.0, -self.segment_spacing),
            270.0: (-self.segment_spacing, 0.0),
        }

        for index in range(length):
            if index == 0:
                block_id = START_LINE
            elif index == length - 1:
                block_id = FINISH_LINE
            elif index % 6 == 0:
                block_id = CHECKPOINT
            elif index % 5 == 0:
                block_id = ROAD_SLOPE
                y += 2.0 if (index // 5) % 2 else -2.0
            elif index % 4 == 0:
                block_id = ROAD_CURVE_90
                rotation = (rotation + 90.0) % 360.0
            else:
                block_id = ROAD_STRAIGHT

            blocks.append(self._block(block_id, x, y, z, rotation))
            if index % 3 == 0 and index not in {0, length - 1}:
                blocks.append(self._block(PILLAR_SQUARE, x - 3.0, y - 6.0, z, rotation))
                blocks.append(self._block(PILLAR_SQUARE, x + 3.0, y - 6.0, z, rotation))

            dx, dz = directions[rotation]
            x += dx
            z += dz

        return blocks

    def _sample_indexes(self, length: int, count: int) -> set[int]:
        candidate_indexes = list(range(1, length - 1))
        self.random.shuffle(candidate_indexes)
        return set(sorted(candidate_indexes[:count]))


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
    if track == "wild":
        return generator.generate_wild_build(length=18 if length is None else length)
    raise ValueError("track must be one of: simple-circuit, obstacle, wild")


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
        "MEDIUM_BRIDGE": (
            TrackGenerator(seed=456),
            lambda generator: generator.generate_with_obstacles(
                length=10, difficulty="medium"
            ),
        ),
        "AI_WILD_BUILD": (
            TrackGenerator(seed=789),
            lambda generator: generator.generate_wild_build(length=18),
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
        description="Generate PolyTrack 0.5.2-compatible PolyTrack1 codes."
    )
    parser.add_argument(
        "track",
        nargs="?",
        default="all",
        choices=("all", "simple-circuit", "obstacle", "wild"),
        help="Track preset to generate. Use 'all' for verbose sample output.",
    )
    parser.add_argument("--length", type=int, help="Number of road segments to build.")
    parser.add_argument(
        "--difficulty",
        choices=("easy", "medium", "hard"),
        default="medium",
        help="Obstacle density for the bridge preset.",
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
        codes = generate_all_tests(verbose=not args.code_only)
        output = (
            "\n".join(codes.values())
            if args.code_only
            else "\n".join(f"{name}: {code}" for name, code in codes.items())
        )
        if args.code_only:
            print(output)
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

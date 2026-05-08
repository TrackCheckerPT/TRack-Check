from __future__ import annotations

import base64

import msgpack
import zstandard as zstd

from core.analyzer import TrackAnalyzer
from core.decoder import import_polytrack
from core.encoder import (
    DEFAULT_AUTHOR,
    DEFAULT_TRACK_NAME,
    EXPORT_PREFIX,
    TRACK_VERSION,
    export_polytrack,
)
from core.generator import START_LINE, TrackGenerator, generate_code, main
from utils.validator import validate_track
from utils.visualizer import visualize_track_2d


def unpack_polytrack_package(code: str) -> dict:
    payload = code.removeprefix(EXPORT_PREFIX)
    packed = zstd.decompress(base64.b64decode(payload))
    return msgpack.unpackb(packed, raw=False)


def test_polytrack_code_round_trips_generated_circuit() -> None:
    blocks = TrackGenerator(seed=123).generate_simple_circuit(length=8)

    code = export_polytrack(blocks)
    decoded, error = import_polytrack(code)

    assert error is None
    assert code.startswith(EXPORT_PREFIX)
    assert decoded == blocks


def test_encoder_uses_polytrack_052_package_wrapper() -> None:
    blocks = TrackGenerator(seed=123).generate_simple_circuit(length=8)

    package = unpack_polytrack_package(export_polytrack(blocks))

    assert package == {
        "v": TRACK_VERSION,
        "a": DEFAULT_AUTHOR,
        "n": DEFAULT_TRACK_NAME,
        "b": blocks,
    }


def test_decoder_ignores_whitespace_in_codes() -> None:
    blocks = TrackGenerator(seed=123).generate_simple_circuit(length=8)
    code = export_polytrack(blocks)
    wrapped_code = f"\n {code[:16]}\n{code[16:]} \t"

    decoded, error = import_polytrack(wrapped_code)

    assert error is None
    assert decoded == blocks


def test_decoder_rejects_invalid_prefix() -> None:
    decoded, error = import_polytrack("v3not-supported")

    assert decoded == []
    assert error == "Track code must start with PolyTrack1"


def test_generated_obstacle_track_is_deterministic_and_valid() -> None:
    first = TrackGenerator(seed=456).generate_with_obstacles(
        length=10, difficulty="medium"
    )
    second = TrackGenerator(seed=456).generate_with_obstacles(
        length=10, difficulty="medium"
    )

    assert first == second
    assert validate_track(first) is None
    assert TrackAnalyzer(first).get_difficulty() == "medium"


def test_validator_reports_multiple_start_lines() -> None:
    blocks = TrackGenerator(seed=123).generate_simple_circuit(length=5)
    blocks[1][0] = START_LINE

    assert validate_track(blocks) == "Track must contain exactly one start line"


def test_analyzer_estimates_simple_line_length() -> None:
    blocks = TrackGenerator(seed=999, segment_spacing=10).generate_with_obstacles(
        length=4, difficulty="easy"
    )

    assert TrackAnalyzer(blocks).estimate_length() == 30.0


def test_visualizer_marks_start_finish_and_pillars() -> None:
    blocks = TrackGenerator(seed=456).generate_with_obstacles(length=5, difficulty="easy")

    drawing = visualize_track_2d(blocks)

    assert "S" in drawing
    assert "F" in drawing
    assert "P" in drawing


def test_generate_code_returns_a_polytrack_code() -> None:
    code = generate_code("obstacle", length=6, difficulty="easy", seed=42)

    decoded, error = import_polytrack(code)

    assert error is None
    assert code.startswith(EXPORT_PREFIX)
    assert len(decoded) == 8


def test_cli_can_print_code_only(capsys) -> None:
    exit_code = main(["simple-circuit", "--length", "4", "--code-only"])

    output = capsys.readouterr().out.strip()
    assert exit_code == 0
    assert output.startswith(EXPORT_PREFIX)
    assert " " not in output


def test_wild_preset_generates_valid_polytrack_code() -> None:
    code = generate_code("wild", length=12, seed=42)

    decoded, error = import_polytrack(code)

    assert error is None
    assert validate_track(decoded) is None
    assert any(block[0] == 22 for block in decoded)

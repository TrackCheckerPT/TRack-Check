from __future__ import annotations


from core.analyzer import TrackAnalyzer
from core.decoder import import_polytrack
from core.encoder import EXPORT_PREFIX, export_polytrack
from core.generator import TrackGenerator
from utils.validator import validate_track
from utils.visualizer import visualize_track_2d


def test_polytrack_code_round_trips_generated_circuit() -> None:
    blocks = TrackGenerator(seed=123).generate_simple_circuit(length=8)

    code = export_polytrack(blocks)
    decoded, error = import_polytrack(code)

    assert error is None
    assert code.startswith(EXPORT_PREFIX)
    assert decoded == blocks


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
    first = TrackGenerator(seed=456).generate_with_obstacles(length=10, difficulty="medium")
    second = TrackGenerator(seed=456).generate_with_obstacles(length=10, difficulty="medium")

    assert first == second
    assert validate_track(first) is None
    assert TrackAnalyzer(first).get_difficulty() == "medium"


def test_validator_reports_duplicate_ids() -> None:
    blocks = TrackGenerator(seed=123).generate_simple_circuit(length=5)
    blocks[1]["id"] = blocks[0]["id"]

    assert validate_track(blocks) == "Duplicate block id: 0"


def test_analyzer_estimates_simple_line_length() -> None:
    blocks = TrackGenerator(seed=999, segment_spacing=10).generate_with_obstacles(
        length=4, difficulty="easy"
    )

    assert TrackAnalyzer(blocks).estimate_length() == 30.0


def test_visualizer_marks_start_finish_and_obstacles() -> None:
    blocks = TrackGenerator(seed=456).generate_with_obstacles(length=5, difficulty="easy")

    drawing = visualize_track_2d(blocks)

    assert "S" in drawing
    assert "F" in drawing
    assert "X" in drawing


def test_generate_code_returns_a_polytrack_code() -> None:
    code = generate_code("obstacle", length=6, difficulty="easy", seed=42)

    decoded, error = import_polytrack(code)

    assert error is None
    assert code.startswith(EXPORT_PREFIX)
    assert len(decoded) == 7


def test_cli_can_print_code_only(capsys) -> None:
    exit_code = main(["simple-circuit", "--length", "4", "--code-only"])

    output = capsys.readouterr().out.strip()
    assert exit_code == 0
    assert output.startswith(EXPORT_PREFIX)
    assert " " not in output

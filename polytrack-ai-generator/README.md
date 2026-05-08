# PolyTrack AI Generator

Experimental tooling for building and testing generated tracks for Kodub's
PolyTrack. The codec now targets the PolyTrack 0.5.2 export wrapper:

- codes start with `PolyTrack1`;
- payloads are Base64-encoded Zstandard streams;
- decompressed bytes are MessagePack maps with `v`, `a`, `n`, and `b` keys;
- `b` contains compact block arrays shaped as `[ID, X, Y, Z, Rotation]`.

## Supported block IDs

| ID | Name |
| --- | --- |
| `0` | `Road_Straight` |
| `1` | `Road_Curve_90` |
| `5` | `Start_Line` |
| `6` | `Finish_Line` |
| `10` | `Pillar_Square` |
| `12` | `Road_Slope` |
| `22` | `Checkpoint` |

Generated tracks always include exactly one start line and at least one finish
line. The default metadata is author `Zawg` and track name `AI_Wild_Build`.

## What is included

- Deterministic track generation for simple circuits, bridge tracks, and wild
  builds with curves, slopes, checkpoints, and decorative pillars.
- `PolyTrack1` export/import round-trip helpers for generated test fixtures.
- Schema validation for compact block arrays and required start/finish lines.
- Basic analysis and ASCII visualization utilities.
- A pytest suite that locks down the codec and generator behavior.

## Run the tests

```bash
python -m pytest polytrack-ai-generator/tests
```

## Generate sample codes

```bash
cd polytrack-ai-generator
python -m core.generator
```

Generate one copy-ready wild build code:

```bash
python CodeMaker wild --code-only
```

## Codespaces tasks

In GitHub Codespaces or VS Code, use **Terminal > Run Task** and select
`PolyTrack: run tests`, `PolyTrack: generate one code`, or
`PolyTrack: generate sample codes` for the common test-builder workflows.

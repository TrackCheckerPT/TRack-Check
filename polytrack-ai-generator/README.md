# PolyTrack AI Generator

Experimental tooling for building and testing generated tracks for Kodub's
PolyTrack. The current focus is a deterministic test-builder format that uses
the modern `PolyTrack1` prefix and a normalized block schema.

## What is included

- Deterministic track generation for simple circuits and obstacle tracks.
- `PolyTrack1` export/import round-trip helpers for generated test fixtures.
- Schema validation for block IDs, transforms, start blocks, and finish blocks.
- Basic analysis and ASCII visualization utilities.
- A pytest suite that locks down the first codec and generator behavior.

## Run the tests

```bash
python -m pytest polytrack-ai-generator/tests
```

## Generate sample codes

```bash
cd polytrack-ai-generator
python -m core.generator
```

The generated code format is intentionally repository-owned while compatibility
work continues. It should not be treated as a complete implementation of every
official editor feature yet.

# TRack-Check

Track-checking and test-building utilities for generated Kodub PolyTrack tracks.

See [`polytrack-ai-generator/README.md`](polytrack-ai-generator/README.md) for
the current Python test-builder workflow.

## GitHub Codespaces

This repository includes a Codespaces/devcontainer setup. When the codespace is
created or rebuilt, it installs the PolyTrack test-builder requirements from
`polytrack-ai-generator/requirements.txt`.

Useful VS Code tasks are also available from **Terminal > Run Task**:

- `PolyTrack: run tests` runs the pytest suite.
- `PolyTrack: generate sample codes` prints representative `PolyTrack1` sample
  codes and ASCII previews.

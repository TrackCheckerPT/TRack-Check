# TRack-Check

Track-checking and test-building utilities for generated Kodub PolyTrack tracks.

See [`polytrack-ai-generator/README.md`](polytrack-ai-generator/README.md) for
the current Python test-builder workflow.

## Generate one PolyTrack code

From the repository root, run this command to print a single `PolyTrack1...`
code string that you can copy:

```bash
python CodeMaker
```

You can customize the generated track too:

```bash
python CodeMaker obstacle --length 12 --difficulty hard --seed 789 --code-only
```

## GitHub Codespaces

This repository includes a Codespaces/devcontainer setup. When the codespace is
created or rebuilt, it installs the PolyTrack test-builder requirements from
`polytrack-ai-generator/requirements.txt`.

Useful VS Code tasks are also available from **Terminal > Run Task**:

- `PolyTrack: run tests` runs the pytest suite.
- `PolyTrack: generate one code` prints a single copy-ready `PolyTrack1` code.
- `PolyTrack: generate sample codes` prints representative `PolyTrack1` sample
  codes and ASCII previews.

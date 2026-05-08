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
- `PolyTrack: generate one code` prints a single copy-ready `PolyTrack1` code.
- `PolyTrack: generate sample codes` prints representative `PolyTrack1` sample
  codes and ASCII previews.

## Git sync troubleshooting

If VS Code or Codespaces reports that local and remote branches have diverged,
run this once in the terminal before pressing **Sync Changes** again:

```bash
git config pull.rebase false
git pull --no-rebase origin main
```

The devcontainer also applies this repository-local Git setting when it is
created or rebuilt so future **Sync Changes** operations do not fail with Git's
"Need to specify how to reconcile divergent branches" message.

"""Zstandard compatibility module for local tests and devcontainers.

Python 3.14 exposes Zstandard as ``compression.zstd``. Older Python versions
use the third-party ``zstandard`` package from ``requirements.txt``. This module
keeps the project import stable in both places.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_backend() -> ModuleType:
    if sys.version_info >= (3, 14):
        import compression.zstd as backend

        return backend

    current_file = Path(__file__).resolve()
    for path_entry in sys.path:
        if not path_entry:
            continue
        spec = importlib.machinery.PathFinder.find_spec("zstandard", [path_entry])
        if spec is None or spec.origin is None:
            continue
        if Path(spec.origin).resolve() == current_file:
            continue
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            continue
        spec.loader.exec_module(module)
        return module

    raise ImportError("Install the 'zstandard' package on Python versions before 3.14")


_backend = _load_backend()
ZstdError = _backend.ZstdError
compress = _backend.compress
decompress = _backend.decompress


class ZstdCompressor:
    """Compatibility wrapper exposing the common compressor API."""

    def __init__(self, level: int = 3) -> None:
        self.level = level

    def compress(self, data: bytes) -> bytes:
        return compress(data, level=self.level)


class ZstdDecompressor:
    """Compatibility wrapper exposing the common decompressor API."""

    def decompress(self, data: bytes) -> bytes:
        return decompress(data)

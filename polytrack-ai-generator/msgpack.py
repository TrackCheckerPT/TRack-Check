"""Minimal MessagePack support for PolyTrack metadata packages.

This implements the subset needed by the generator: dictionaries with string
keys, arrays, strings, integers, and 64-bit floats. It intentionally mirrors the
``msgpack`` package's ``packb``/``unpackb`` functions used by the app.
"""

from __future__ import annotations

import struct
from typing import Any


class FormatError(ValueError):
    """Raised when MessagePack bytes cannot be parsed."""


class ExtraData(ValueError):
    """Raised when bytes remain after parsing one MessagePack object."""


def packb(value: Any, *, use_bin_type: bool = True) -> bytes:
    """Pack a Python value into MessagePack bytes."""

    return _pack(value)


def unpackb(data: bytes, *, raw: bool = False) -> Any:
    """Unpack exactly one MessagePack object from bytes."""

    value, offset = _unpack(data, 0, raw=raw)
    if offset != len(data):
        raise ExtraData("unpack(b) received extra data")
    return value


def _pack(value: Any) -> bytes:
    if isinstance(value, dict):
        items = list(value.items())
        prefix = _pack_length(len(items), fix_base=0x80, max_fix=15, code8=0xDE)
        return prefix + b"".join(_pack(key) + _pack(item) for key, item in items)
    if isinstance(value, (list, tuple)):
        prefix = _pack_length(len(value), fix_base=0x90, max_fix=15, code8=0xDC)
        return prefix + b"".join(_pack(item) for item in value)
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        length = len(encoded)
        if length <= 31:
            return bytes([0xA0 | length]) + encoded
        if length <= 0xFF:
            return b"\xD9" + struct.pack(">B", length) + encoded
        if length <= 0xFFFF:
            return b"\xDA" + struct.pack(">H", length) + encoded
        raise ValueError("MessagePack string is too large")
    if isinstance(value, bool):
        return b"\xC3" if value else b"\xC2"
    if isinstance(value, int):
        if 0 <= value <= 0x7F:
            return bytes([value])
        if -32 <= value < 0:
            return bytes([0x100 + value])
        if 0 <= value <= 0xFF:
            return b"\xCC" + struct.pack(">B", value)
        if 0 <= value <= 0xFFFF:
            return b"\xCD" + struct.pack(">H", value)
        if -(2**31) <= value <= (2**31 - 1):
            return b"\xD2" + struct.pack(">i", value)
    if isinstance(value, float):
        return b"\xCB" + struct.pack(">d", value)
    raise TypeError(f"Cannot MessagePack encode {type(value).__name__}")


def _pack_length(length: int, *, fix_base: int, max_fix: int, code8: int) -> bytes:
    if length <= max_fix:
        return bytes([fix_base | length])
    if length <= 0xFFFF:
        return bytes([code8]) + struct.pack(">H", length)
    raise ValueError("MessagePack object is too large")


def _unpack(data: bytes, offset: int, *, raw: bool) -> tuple[Any, int]:
    if offset >= len(data):
        raise FormatError("Unexpected end of MessagePack data")

    marker = data[offset]
    offset += 1

    if marker <= 0x7F:
        return marker, offset
    if marker >= 0xE0:
        return marker - 0x100, offset
    if 0x80 <= marker <= 0x8F:
        return _unpack_map(data, offset, marker & 0x0F, raw=raw)
    if 0x90 <= marker <= 0x9F:
        return _unpack_array(data, offset, marker & 0x0F, raw=raw)
    if 0xA0 <= marker <= 0xBF:
        return _unpack_string(data, offset, marker & 0x1F, raw=raw)
    if marker == 0xC2:
        return False, offset
    if marker == 0xC3:
        return True, offset
    if marker == 0xCB:
        return _read_struct(data, offset, ">d")
    if marker == 0xCC:
        return _read_struct(data, offset, ">B")
    if marker == 0xCD:
        return _read_struct(data, offset, ">H")
    if marker == 0xD2:
        return _read_struct(data, offset, ">i")
    if marker == 0xD9:
        length, offset = _read_struct(data, offset, ">B")
        return _unpack_string(data, offset, length, raw=raw)
    if marker == 0xDA:
        length, offset = _read_struct(data, offset, ">H")
        return _unpack_string(data, offset, length, raw=raw)
    if marker == 0xDC:
        length, offset = _read_struct(data, offset, ">H")
        return _unpack_array(data, offset, length, raw=raw)
    if marker == 0xDE:
        length, offset = _read_struct(data, offset, ">H")
        return _unpack_map(data, offset, length, raw=raw)

    raise FormatError(f"Unsupported MessagePack marker: 0x{marker:02x}")


def _unpack_array(data: bytes, offset: int, length: int, *, raw: bool) -> tuple[list[Any], int]:
    values = []
    for _ in range(length):
        value, offset = _unpack(data, offset, raw=raw)
        values.append(value)
    return values, offset


def _unpack_map(data: bytes, offset: int, length: int, *, raw: bool) -> tuple[dict[Any, Any], int]:
    values = {}
    for _ in range(length):
        key, offset = _unpack(data, offset, raw=raw)
        value, offset = _unpack(data, offset, raw=raw)
        values[key] = value
    return values, offset


def _unpack_string(data: bytes, offset: int, length: int, *, raw: bool) -> tuple[str | bytes, int]:
    end = offset + length
    if end > len(data):
        raise FormatError("Unexpected end of MessagePack string")
    value = data[offset:end]
    return (value if raw else value.decode("utf-8")), end


def _read_struct(data: bytes, offset: int, fmt: str) -> tuple[Any, int]:
    size = struct.calcsize(fmt)
    end = offset + size
    if end > len(data):
        raise FormatError("Unexpected end of MessagePack data")
    return struct.unpack(fmt, data[offset:end])[0], end

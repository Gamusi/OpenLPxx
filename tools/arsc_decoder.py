#!/usr/bin/env python3
"""Minimal pure-Python decoder for Android compiled resources.arsc files."""

from __future__ import annotations

import struct
from typing import Any

RES_STRING_POOL_TYPE = 0x0001
RES_TABLE_TYPE = 0x0002
RES_TABLE_PACKAGE_TYPE = 0x0200
RES_TABLE_TYPE_TYPE = 0x0201

TYPE_STRING = 0x03
FLAG_COMPLEX = 0x0001
FLAG_SPARSE = 0x01
FLAG_OFFSET16 = 0x02
NO_ENTRY = 0xFFFFFFFF


def _read_utf8_len(data: bytes, pos: int) -> tuple[int, int]:
    first = data[pos]
    pos += 1
    if first & 0x80:
        second = data[pos]
        pos += 1
        return ((first & 0x7F) << 8) | second, pos
    return first, pos


def _read_utf16_len(data: bytes, pos: int) -> tuple[int, int]:
    first = struct.unpack_from("<H", data, pos)[0]
    pos += 2
    if first & 0x8000:
        second = struct.unpack_from("<H", data, pos)[0]
        pos += 2
        return ((first & 0x7FFF) << 16) | second, pos
    return first, pos


def _parse_string_pool(data: bytes, offset: int) -> list[str]:
    chunk_type, header_size, chunk_size = struct.unpack_from("<HHI", data, offset)
    if chunk_type != RES_STRING_POOL_TYPE:
        raise ValueError(f"Expected string pool chunk (0x0001), got 0x{chunk_type:04x}")
    string_count, _style_count, flags, strings_start, _styles_start = struct.unpack_from(
        "<IIIII", data, offset + 8
    )
    is_utf8 = bool(flags & (1 << 8))
    offsets_base = offset + header_size
    pool_base = offset + strings_start

    strings: list[str] = []
    for idx in range(string_count):
        str_rel = struct.unpack_from("<I", data, offsets_base + idx * 4)[0]
        pos = pool_base + str_rel
        if is_utf8:
            _char_len, pos = _read_utf8_len(data, pos)
            byte_len, pos = _read_utf8_len(data, pos)
            strings.append(data[pos : pos + byte_len].decode("utf-8", errors="replace"))
        else:
            char_len, pos = _read_utf16_len(data, pos)
            strings.append(data[pos : pos + char_len * 2].decode("utf-16-le", errors="replace"))
    return strings


def _decode_locale(config_bytes: bytes) -> str:
    if len(config_bytes) < 8:
        return "default"
    lang = config_bytes[4:6]
    country = config_bytes[6:8]
    lang_str = lang.decode("ascii", errors="ignore").strip("\x00")
    country_str = country.decode("ascii", errors="ignore").strip("\x00")
    if not lang_str:
        return "default"
    return f"{lang_str}-{country_str}" if country_str else lang_str


def decode_arsc(data: bytes) -> dict[str, Any]:
    """Decode strings and string-arrays from a compiled resources.arsc buffer."""
    chunk_type, header_size, total_size = struct.unpack_from("<HHI", data, 0)
    if chunk_type != RES_TABLE_TYPE:
        raise ValueError(f"Invalid resources.arsc header type: 0x{chunk_type:04x}")

    pos = header_size
    global_strings: list[str] = []
    strings_out: dict[str, dict[str, Any]] = {}
    arrays_out: dict[str, dict[str, Any]] = {}

    while pos + 8 <= min(total_size, len(data)):
        c_type, c_hdr, c_size = struct.unpack_from("<HHI", data, pos)
        if c_size == 0:
            break
        if c_type == RES_STRING_POOL_TYPE and not global_strings:
            global_strings = _parse_string_pool(data, pos)
        elif c_type == RES_TABLE_PACKAGE_TYPE:
            _decode_package(data, pos, c_hdr, c_size, global_strings, strings_out, arrays_out)
        pos += c_size

    return {"strings": strings_out, "arrays": arrays_out}


def _decode_package(
    data: bytes,
    pkg_offset: int,
    pkg_hdr_size: int,
    pkg_size: int,
    global_strings: list[str],
    strings_out: dict[str, dict[str, Any]],
    arrays_out: dict[str, dict[str, Any]],
) -> None:
    pkg_id = struct.unpack_from("<I", data, pkg_offset + 8)[0]
    type_strings_rel, _last_pub_type, key_strings_rel = struct.unpack_from(
        "<III", data, pkg_offset + 268
    )
    type_names = _parse_string_pool(data, pkg_offset + type_strings_rel) if type_strings_rel else []
    key_names = _parse_string_pool(data, pkg_offset + key_strings_rel) if key_strings_rel else []

    pos = pkg_offset + pkg_hdr_size
    pkg_end = pkg_offset + pkg_size
    while pos + 8 <= pkg_end:
        c_type, c_hdr, c_size = struct.unpack_from("<HHI", data, pos)
        if c_size == 0:
            break
        if c_type == RES_TABLE_TYPE_TYPE:
            _decode_type_chunk(
                data, pos, c_hdr, c_size, pkg_id, type_names, key_names,
                global_strings, strings_out, arrays_out,
            )
        pos += c_size


def _decode_type_chunk(
    data: bytes,
    offset: int,
    hdr_size: int,
    _chunk_size: int,
    pkg_id: int,
    type_names: list[str],
    key_names: list[str],
    global_strings: list[str],
    strings_out: dict[str, dict[str, Any]],
    arrays_out: dict[str, dict[str, Any]],
) -> None:
    type_id, flags, _res, entry_count, entries_start = struct.unpack_from("<BBHII", data, offset + 8)
    type_name = type_names[type_id - 1] if 0 < type_id <= len(type_names) else f"type_{type_id}"
    if type_name not in ("string", "array"):
        return

    locale = _decode_locale(data[offset + 20 : offset + hdr_size])
    offsets_base = offset + hdr_size
    entries_base = offset + entries_start

    for idx in range(entry_count):
        if flags & FLAG_SPARSE:
            entry_idx, rel16 = struct.unpack_from("<HH", data, offsets_base + idx * 4)
            if rel16 == 0xFFFF:
                continue
            entry_pos = entries_base + rel16 * 4
        elif flags & FLAG_OFFSET16:
            entry_idx = idx
            rel16 = struct.unpack_from("<H", data, offsets_base + idx * 2)[0]
            if rel16 == 0xFFFF:
                continue
            entry_pos = entries_base + rel16 * 4
        else:
            entry_idx = idx
            rel32 = struct.unpack_from("<I", data, offsets_base + idx * 4)[0]
            if rel32 == NO_ENTRY:
                continue
            entry_pos = entries_base + rel32

        if entry_pos + 8 > len(data):
            continue
        e_size, e_flags, key_idx = struct.unpack_from("<HHI", data, entry_pos)
        key_name = key_names[key_idx] if key_idx < len(key_names) else f"res_{entry_idx}"
        res_id = f"0x{(pkg_id << 24) | (type_id << 16) | entry_idx:08x}"

        if (e_flags & FLAG_COMPLEX) == 0 and type_name == "string":
            val_pos = entry_pos + e_size
            _v_size, _res0, data_type, val_data = struct.unpack_from("<HBBI", data, val_pos)
            if data_type == TYPE_STRING and val_data < len(global_strings):
                # Prefer default locale or keep first non-empty
                if key_name not in strings_out or locale == "default":
                    strings_out[key_name] = {
                        "id": res_id,
                        "key": key_name,
                        "locale": locale,
                        "value": global_strings[val_data],
                    }
        elif (e_flags & FLAG_COMPLEX) != 0 and type_name == "array":
            _parent, item_count = struct.unpack_from("<II", data, entry_pos + 8)
            items: list[str] = []
            item_pos = entry_pos + e_size
            for _ in range(item_count):
                if item_pos + 12 > len(data):
                    break
                _name_id, v_size, _res0, data_type, val_data = struct.unpack_from("<IHBBI", data, item_pos)
                if data_type == TYPE_STRING and val_data < len(global_strings):
                    items.append(global_strings[val_data])
                item_pos += 4 + v_size
            if items and (key_name not in arrays_out or locale == "default"):
                arrays_out[key_name] = {
                    "id": res_id,
                    "key": key_name,
                    "locale": locale,
                    "items": items,
                }

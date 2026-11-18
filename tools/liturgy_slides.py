#!/usr/bin/env python3
"""Pure transformation and eligibility helpers for Come and Worship Custom Slides."""

from __future__ import annotations

import re
from typing import Any

EXCLUDED_KEYS = frozenset({"story1", "story2", "story3"})
SPEAKER_PREFIX = re.compile(r"^(Leader|People|Minister|Congregation|Reader|All)\s*:")


def select_eligible_entries(
    entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split index entries into (eligible, excluded) without inventing content."""
    eligible: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for entry in entries:
        key = entry.get("resource_key", "")
        cat = entry.get("category", "")
        if key in EXCLUDED_KEYS or cat == "front_matter":
            excluded.append(entry)
        else:
            eligible.append(entry)
    return eligible, excluded


def build_searchable_title(entry: dict[str, Any], raw_text: str) -> str:
    """Create a descriptive, searchable title preserving original wording."""
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    base = (entry.get("title") or (lines[0] if lines else entry["resource_key"])).strip()
    if base.upper() == "ORDER OF SERVICE FOR" and len(lines) > 1:
        base = f"{base} {lines[1]}"
    elif base.upper().startswith("APPENDIX ") and len(lines) > 1:
        base = f"{base}: {lines[1]}"
    elif base.upper().startswith("THEN THE LEADER"):
        base = "Morning & Evening Prayer — Opening Sentences"
    return f"{base} (Come and Worship)"


def split_into_slides(
    raw_text: str,
    max_lines: int = 10,
    max_chars: int = 480,
) -> list[str]:
    """Divide liturgical text deterministically at paragraph/speaker boundaries."""
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", normalized) if p.strip()]
    chunks: list[str] = []
    for para in paragraphs:
        p_lines = [ln.rstrip() for ln in para.split("\n") if ln.strip()]
        if len(p_lines) <= max_lines and len(para) <= max_chars:
            chunks.append("\n".join(p_lines))
            continue

        current: list[str] = []
        current_chars = 0
        for line in p_lines:
            is_speaker = bool(SPEAKER_PREFIX.match(line.lstrip()))
            would_exceed = (
                len(current) >= max_lines
                or (current_chars + len(line) + 1 > max_chars and (is_speaker or len(current) >= 4))
            )
            if current and would_exceed:
                chunks.append("\n".join(current))
                current = [line]
                current_chars = len(line)
            else:
                current.append(line)
                current_chars += len(line) + 1
        if current:
            chunks.append("\n".join(current))

    return chunks

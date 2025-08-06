"""Utility helpers."""

from __future__ import annotations

import hashlib


def hash_text(text: str) -> str:
    """Return SHA256 hash of text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

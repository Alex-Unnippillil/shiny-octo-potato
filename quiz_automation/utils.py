"""Miscellaneous utility helpers."""
from __future__ import annotations

import hashlib


def question_hash(text: str) -> str:
    """Return a stable SHA256 hash for a question string."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()

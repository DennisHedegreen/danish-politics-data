from __future__ import annotations

from pathlib import Path


def resolve_sweden_public_path(relative_path: str, variant: str = "") -> Path:
    return Path("sweden") / relative_path

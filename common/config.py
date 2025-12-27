from __future__ import annotations
from pathlib import Path
from functools import lru_cache


def _find_project_root(start: Path) -> Path:
    """
    Walk upward until we find 'config.txt'. This allows running uvicorn from
    different working directories.
    """
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / "config.txt").exists():
            return p
    # Fallback: assume current working directory is project root
    return Path.cwd().resolve()


@lru_cache(maxsize=1)
def get_oop_enabled(default: bool = True) -> bool:
    """
    Reads config.txt and returns True if oop_enabled=1, else False.

    config.txt is expected to be located in src/ (project root).
    Example: oop_enabled=1
    """
    root = _find_project_root(Path(__file__).parent)
    cfg = root / "config.txt"
    if not cfg.exists():
        return default

    text = cfg.read_text(encoding="utf-8", errors="ignore")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = [x.strip() for x in line.split("=", 1)]
        if k.lower() == "oop_enabled":
            return v in ("1", "true", "yes", "on", "True", "TRUE")
    return default

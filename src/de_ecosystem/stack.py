"""The declarative data stack, loaded from stack.yaml.

One file describes the whole pipeline — engine, sources, and the momentum metric.
Precedence: environment variable > stack.yaml > built-in default, so the YAML is
the readable source of truth while env vars still override for one-off runs.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from de_ecosystem.config import DE_TOOLS

STACK_FILE = "stack.yaml"


@dataclass
class Stack:
    engine: str = "datafusion"
    db_path: str = "de_ecosystem.duckdb"
    bsky_max_pages: int = 40
    github_slice: str = "data/raw/gharchive/*.json.gz"
    window_days: int = 90
    tools: list[str] = field(default_factory=lambda: list(DE_TOOLS))


def load_stack(path: str = STACK_FILE) -> Stack:
    data: dict = {}
    p = Path(path)
    if p.exists():
        data = yaml.safe_load(p.read_text()) or {}
    sources = data.get("sources") or {}
    bsky = sources.get("bluesky") or {}
    github = sources.get("github") or {}
    momentum = data.get("momentum") or {}
    return Stack(
        engine=data.get("engine") or "datafusion",
        db_path=data.get("db_path") or "de_ecosystem.duckdb",
        bsky_max_pages=int(os.getenv("DE_BSKY_MAX_PAGES") or bsky.get("max_pages") or 40),
        github_slice=github.get("slice") or "data/raw/gharchive/*.json.gz",
        window_days=int(os.getenv("DE_WINDOW_DAYS") or momentum.get("window_days") or 90),
        tools=list(momentum.get("tools") or DE_TOOLS),
    )


stack = load_stack()

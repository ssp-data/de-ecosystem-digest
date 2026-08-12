"""Register curated expressions as versioned entries in the local xorq catalog.

Run with: make catalog

Each curated expression from expr.py is added to the ./catalog store — a
git-backed, content-addressed catalog. xorq bundles the source read at build
time, so every entry is reproducible with `xorq catalog run <alias>` without
re-running ingest. Editing an expression changes its content hash, which
registers a new versioned entry (the old one stays retrievable).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # repo root for `expr`

import expr as e  # noqa: E402
from xorq.catalog.api import Catalog  # noqa: E402

CATALOG_PATH = Path("catalog")


def register() -> None:
    catalog = Catalog.from_repo_path(CATALOG_PATH)  # init=None → create if absent, else open
    print(f"catalog: {CATALOG_PATH.resolve()}\n")
    for alias, varname in e.CATALOG_ENTRIES.items():
        expr = getattr(e, varname, None)
        if expr is None:
            print(f"  skip  {alias:20} (source table not populated)")
            continue
        entry = catalog.add(expr, aliases=(alias,), sync=False, exist_ok=True)
        print(f"  add   {alias:20} → {entry.name}  {tuple(entry.columns)}")


if __name__ == "__main__":
    register()

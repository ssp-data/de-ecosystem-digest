import time

import duckdb
import requests
from de_ecosystem.config import DE_TOOLS
from de_ecosystem.settings import settings

PYPISTATS_URL = "https://pypistats.org/api/packages/{package}/overall"
MAX_RETRIES = 4


def _fetch_overall(package: str) -> list[dict]:
    """Fetch download stats with backoff — pypistats.org rate-limits bursts."""
    for attempt in range(MAX_RETRIES):
        resp = requests.get(PYPISTATS_URL.format(package=package), timeout=15)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** (attempt + 1)))
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json().get("data", [])
    raise RuntimeError(f"rate-limited after {MAX_RETRIES} attempts")


def load_pypi(db_path: str = settings.db_path, packages: list[str] | None = None) -> None:
    """Load PyPI download stats from pypistats.org into DuckDB (idempotent upsert)."""
    packages = packages or DE_TOOLS
    con = duckdb.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_pypi_downloads (
            category    TEXT,
            date        DATE,
            downloads   BIGINT,
            package     TEXT,
            PRIMARY KEY (package, date, category)
        )
    """)
    failed = []
    for package in packages:
        try:
            for row in _fetch_overall(package):
                con.execute(
                    """
                    INSERT OR REPLACE INTO raw_pypi_downloads
                        (category, date, downloads, package)
                    VALUES (?, ?, ?, ?)
                    """,
                    [row["category"], row["date"], row["downloads"], package],
                )
        except Exception as exc:
            failed.append(package)
            print(f"WARNING: pypi fetch failed for {package}: {exc}")
    if failed:
        print(f"WARNING: {len(failed)}/{len(packages)} packages missing: {', '.join(failed)}")
    con.close()

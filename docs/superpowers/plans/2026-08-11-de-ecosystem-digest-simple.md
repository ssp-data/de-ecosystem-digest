# De Ecosystem Digest (Simple) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a small, readable xorq project that produces a Data Engineering Ecosystem "momentum" digest and demonstrates the grammar of data (noun → verb → template → modifier → manifest → execute) from Part 1.

**Architecture:** dlt ingests four public signals (RSS, Bluesky, PyPI, GitHub) into a local DuckDB file — imperative, *outside* the grammar. xorq `catalog/` expressions read those tables and produce named, executable, manifestable expressions. `digest.py` prints the headline momentum leaderboard; `make engines` runs the same expression on DuckDB/DataFusion/Snowflake; ML reframes `fit` as a modifier and `predict` as a verb. A set of pedagogical Makefile targets (`make noun/verb/template/modifier/manifest/run-sentence`) turns the Makefile itself into the grammar.

**Tech Stack:** Python 3.13, uv, xorq (Ibis + DataFusion), dlt, DuckDB, scikit-learn, feedparser, requests, pytest.

**Working directory:** `/home/sspaeti/Documents/work/xorq/de-ecosystem-digest-simple` (already a git repo with `.env`, `.gitignore`). The reference/original repo is `/home/sspaeti/Documents/work/xorq/de-ecosystem-digest` — used only to copy code and data from.

**Conventions:** All commands run from the project root. Package import root is `de_ecosystem` under `src/`. Run Python via `uv run`. Commit after each task.

---

## Task 1: Project scaffold (packaging, ignore, env)

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.env.example`
- Modify: `.gitignore`
- Create: `src/de_ecosystem/__init__.py` (empty)
- Create: `src/de_ecosystem/ingest/__init__.py` (empty)
- Create: `src/de_ecosystem/catalog/__init__.py` (empty)
- Create: `src/de_ecosystem/ml/__init__.py` (empty)

- [ ] **Step 1: Create `pyproject.toml`** (drop `boring-semantic-layer`; keep the rest)

```toml
[project]
name = "de-ecosystem-digest-simple"
version = "0.1.0"
description = "A minimal xorq project: DE ecosystem momentum digest, demonstrating the grammar of data"
requires-python = ">=3.13"
dependencies = [
    "xorq>=0.1.0",
    "dlt[duckdb]>=1.18",
    "feedparser>=6.0",
    "requests>=2.31",
    "pydantic-settings>=2.0",
    "scikit-learn>=1.4",
    "pandas>=2.2",
    "numpy>=1.26",
    "enlighten>=1.12",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-mock>=3.12",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/de_ecosystem"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `.python-version`**

```
3.13
```

- [ ] **Step 3: Create `.env.example`** (engine switching only — no DEV/PROD, no BigQuery/MotherDuck)

```
# Which engine catalog expressions execute on: duckdb | datafusion | snowflake
DE_ENGINE=datafusion
DE_DB_PATH=de_ecosystem.duckdb

# Optional Bluesky DE feed URI (at://did:plc:.../app.bsky.feed.generator/...)
DE_BSKY_FEED_URI=

# Snowflake — only needed for `make engines` to include Snowflake.
# xorq reads these via xo.snowflake.connect_env().
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_ROLE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_SCHEMA=PUBLIC
```

- [ ] **Step 4: Overwrite `.gitignore`**

```
# Python
__pycache__/
*.pyc
.venv/
.pytest_cache/
.mypy_cache/

# Secrets
.env

# Data — ingested locally, not committed (except the small gharchive slice)
de_ecosystem.duckdb
de_ecosystem.duckdb.wal
data/raw/gharchive/*.json.gz
!data/raw/gharchive/de-slice.json.gz
archive/

# xorq builds — commit ONE artifact by force-add for the manifest-diff demo
builds/
```

- [ ] **Step 5: Create the four empty `__init__.py` package files**

Create `src/de_ecosystem/__init__.py`, `src/de_ecosystem/ingest/__init__.py`, `src/de_ecosystem/catalog/__init__.py`, `src/de_ecosystem/ml/__init__.py`, each empty.

- [ ] **Step 6: Install and verify the environment resolves**

Run: `uv sync --extra dev`
Expected: resolves and installs without error; creates `.venv/` and `uv.lock`.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .python-version .env.example .gitignore src uv.lock
git commit -m "chore: scaffold simple de-ecosystem-digest package"
```

---

## Task 2: `config.py` (feeds, repos, tools)

**Files:**
- Create: `src/de_ecosystem/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from de_ecosystem import config


def test_config_lists_are_populated():
    assert len(config.DE_FEEDS) > 30
    assert len(config.DE_TOOLS) >= 15
    assert len(config.DE_REPOS) >= 15
    assert "pydantic" in config.DE_TOOLS          # the "raw downloads lie" example
    assert "xorq-labs/xorq" in config.DE_REPOS
    assert config.BSKY_SOURCES and all(s.startswith("at://") for s in config.BSKY_SOURCES)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'de_ecosystem.config'`

- [ ] **Step 3: Create `config.py`**

Copy the file verbatim from the reference repo: `/home/sspaeti/Documents/work/xorq/de-ecosystem-digest/src/de_ecosystem/config.py`. It defines `VENDOR_FEEDS`, `COMMUNITY_FEEDS`, `DE_FEEDS = VENDOR_FEEDS + COMMUNITY_FEEDS`, `BSKY_SOURCES`, `DE_REPOS`, and `DE_TOOLS` (which includes `"pydantic"`). No changes.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/de_ecosystem/config.py tests/test_config.py
git commit -m "feat: port config (feeds, repos, tools)"
```

---

## Task 3: `settings.py` (engine switching + DuckDB→backend bridge)

This replaces the original DEV/PROD settings with a single **engine** switch (duckdb | datafusion | snowflake). No BigQuery, no MotherDuck.

**Files:**
- Create: `src/de_ecosystem/settings.py`
- Test: `tests/test_settings.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_settings.py
import pandas as pd
from de_ecosystem.settings import Settings


def test_default_engine_is_datafusion():
    assert Settings().engine == "datafusion"


def test_backend_duckdb_and_datafusion_run_same_expression():
    s = Settings()
    for engine in ("datafusion", "duckdb"):
        con = s.backend(engine)
        con.create_table("t", pd.DataFrame({"x": [1, 2, 3]}), overwrite=True)
        out = con.table("t").agg(total=con.table("t").x.sum()).execute()
        assert int(out["total"].iloc[0]) == 6


def test_load_tables_skips_missing_silently(tmp_path):
    s = Settings(db_path=str(tmp_path / "empty.duckdb"))
    con = s.backend("datafusion")
    s.load_tables_to_backend(con)  # no DuckDB file/tables yet — must not raise
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_settings.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'de_ecosystem.settings'`

- [ ] **Step 3: Create `settings.py`**

```python
from __future__ import annotations
from typing import Any, Literal
from pydantic_settings import BaseSettings
import duckdb
import xorq.api as xo

# Tables written by the dlt ingest layer that catalog expressions read.
RAW_TABLES = ["articles", "posts", "raw_pypi_downloads", "raw_github_events"]

Engine = Literal["duckdb", "datafusion", "snowflake"]


class Settings(BaseSettings):
    engine: Engine = "datafusion"
    db_path: str = "de_ecosystem.duckdb"
    bsky_feed_uri: str = ""

    model_config = {"env_prefix": "DE_", "env_file": ".env", "extra": "ignore"}

    def backend(self, engine: Engine | None = None) -> Any:
        """Return a xorq backend for the given engine (defaults to settings.engine).

        Snowflake reads credentials from SNOWFLAKE_* env vars via connect_env().
        """
        engine = engine or self.engine
        if engine == "duckdb":
            return xo.duckdb.connect()
        if engine == "snowflake":
            return xo.snowflake.connect_env()
        return xo.connect()  # datafusion (embedded default)

    def duck_connection(self) -> duckdb.DuckDBPyConnection:
        """Raw DuckDB connection — used by the ingest layer to write raw tables."""
        return duckdb.connect(self.db_path)

    def load_tables_to_backend(self, con: Any, tables: list[str] = RAW_TABLES) -> None:
        """Bridge: copy dlt-written DuckDB tables into the chosen xorq backend.

        Missing tables (nothing ingested yet) are skipped silently so the
        catalog demos degrade to "(no data)" rather than crashing.
        """
        duck = self.duck_connection()
        for table in tables:
            try:
                df = duck.execute(f"SELECT * FROM {table}").df()
                con.create_table(table, df, overwrite=True)
            except Exception:
                pass
        duck.close()

    def github_data_glob(self) -> str:
        return "data/raw/gharchive/*.json.gz"


settings = Settings()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_settings.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/de_ecosystem/settings.py tests/test_settings.py
git commit -m "feat: settings with engine switching and DuckDB->backend bridge"
```

---

## Task 4: Test fixtures (`conftest.py`)

Provides the seeded `con` fixture (DataFusion backend with all four raw tables) so every catalog test runs offline. Copied from the reference repo's `tests/conftest.py`.

**Files:**
- Create: `tests/__init__.py` (empty)
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `tests/__init__.py`** (empty file)

- [ ] **Step 2: Create `tests/conftest.py`**

Copy verbatim from `/home/sspaeti/Documents/work/xorq/de-ecosystem-digest/tests/conftest.py`. It defines a `con` fixture on `xo.connect()` seeded via `_seed_articles`, `_seed_pypi` (90 days of `dbt-core` + `polars`), `_seed_github` (30 days of `WatchEvent`/`PullRequestEvent` for `dbt-labs/dbt-core` plus one `pola-rs/polars`), and `_seed_posts` (3 Bluesky posts with hashtags). No changes.

- [ ] **Step 3: Verify the fixture imports cleanly**

Run: `uv run python -c "import tests.conftest"`
Expected: no output, exit 0.

- [ ] **Step 4: Commit**

```bash
git add tests/__init__.py tests/conftest.py
git commit -m "test: seeded backend fixtures for offline catalog tests"
```

---

## Task 5: Catalog — articles expressions

**Files:**
- Create: `src/de_ecosystem/catalog/articles.py`
- Test: `tests/test_catalog_articles.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_catalog_articles.py
from de_ecosystem.catalog.articles import tool_mention_frequency, source_output_rate


def test_tool_mention_frequency_counts_dbt(con):
    df = tool_mention_frequency(con, "dbt").execute()
    assert df["mentions"].sum() >= 1
    assert set(df.columns) == {"week", "mentions"}


def test_source_output_rate_has_per_week_column(con):
    df = source_output_rate(con).execute()
    assert "articles_per_week" in df.columns
    assert (df["articles_per_week"] > 0).all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_catalog_articles.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `articles.py`**

Copy verbatim from `/home/sspaeti/Documents/work/xorq/de-ecosystem-digest/src/de_ecosystem/catalog/articles.py` (defines `tool_mention_frequency(con, tool, days=30)` and `source_output_rate(con, days=30)`). No changes.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_catalog_articles.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/de_ecosystem/catalog/articles.py tests/test_catalog_articles.py
git commit -m "feat: catalog articles expressions"
```

---

## Task 6: Catalog — PyPI expressions (+ naive raw-volume for the pydantic callout)

Adds a new `raw_download_volume` expression — the "naive leaderboard" that puts pydantic on top — alongside the ported trend/acceleration expressions.

**Files:**
- Create: `src/de_ecosystem/catalog/pypi.py`
- Test: `tests/test_catalog_pypi.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_catalog_pypi.py
from de_ecosystem.catalog.pypi import (
    download_trend_90d,
    adoption_acceleration,
    raw_download_volume,
)


def test_download_trend_returns_ordered_series(con):
    df = download_trend_90d(con, "dbt-core").execute()
    assert set(df.columns) == {"date", "downloads", "package"}
    assert df["date"].is_monotonic_increasing


def test_adoption_acceleration_positive_for_growing_series(con):
    # conftest seeds dbt-core downloads increasing with age index -> positive slope
    df = adoption_acceleration(con, "dbt-core").execute()
    assert "slope" in df.columns


def test_raw_download_volume_ranks_by_total(con):
    df = raw_download_volume(con).execute()
    assert list(df.columns) == ["package", "downloads"]
    assert df["downloads"].is_monotonic_decreasing
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_catalog_pypi.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `pypi.py`**

Copy `download_trend_90d` and `adoption_acceleration` verbatim from the reference repo's `catalog/pypi.py`, then append the new `raw_download_volume` expression:

```python
def raw_download_volume(
    con: object,
    days: int = 180,
) -> object:
    """Naive leaderboard: total downloads per package (without mirrors), last N days.

    This is the 'wrong' ranking the post opens with — pydantic dominates because
    it's a transitive dependency of half of PyData, not a DE tool with momentum.
    """
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=days)).date()
    t = con.table("raw_pypi_downloads")
    return (
        t.filter([
            t.category == "without_mirrors",
            t.date > cutoff,
        ])
        .group_by("package")
        .agg(downloads=t.downloads.sum())
        .order_by(xo._.downloads.desc())  # order by the aggregated output column
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_catalog_pypi.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/de_ecosystem/catalog/pypi.py tests/test_catalog_pypi.py
git commit -m "feat: catalog pypi expressions + naive raw_download_volume"
```

---

## Task 7: Catalog — GitHub expressions (the grammar anchor)

`star_velocity_30d` is the pedagogical centerpiece. Add inline parts-of-speech comments so the source doubles as teaching material.

**Files:**
- Create: `src/de_ecosystem/catalog/github.py`
- Test: `tests/test_catalog_github.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_catalog_github.py
from de_ecosystem.catalog.github import star_velocity_30d, pr_merge_rate


def test_star_velocity_counts_watch_events(con):
    df = star_velocity_30d(con, "dbt-labs/dbt-core").execute()
    assert set(df.columns) == {"week", "stars"}
    assert df["stars"].sum() >= 1


def test_pr_merge_rate_counts_pr_events(con):
    df = pr_merge_rate(con, "dbt-labs/dbt-core").execute()
    assert int(df["total_prs"].iloc[0]) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_catalog_github.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `github.py`** (ported, with parts-of-speech comments added)

```python
from datetime import datetime, timedelta
import xorq.api as xo


def star_velocity_30d(
    con: object,   # TEMPLATE: (con, repo) — bind this sentence to any repo later
    repo: str,
) -> object:
    """Stars gained per week over the last 30 days (WatchEvent = a GitHub star).

    The grammar, labeled:
      noun     -> con.table("raw_github_events")   (a lazy pointer, no compute)
      verbs    -> .filter -> .mutate -> .group_by -> .agg -> .order_by
      template -> the (con, repo) signature binds to dbt-core, polars, ...
      modifier -> which engine executes it (DuckDB / DataFusion / Snowflake)
    """
    cutoff = datetime.now() - timedelta(days=30)
    t = con.table("raw_github_events")                       # noun
    return (
        t.filter([                                           # verb
            t.repo_name == repo,
            t.type == "WatchEvent",
            t.created_at > cutoff,
        ])
        .mutate(week=t.created_at.truncate("W"))             # verb
        .group_by("week")                                    # verb
        .agg(stars=t.id.count())                             # verb
        .order_by("week")                                    # verb
    )


def pr_merge_rate(
    con: object,
    repo: str,
    days: int = 30,
) -> object:
    """Count of PR events in the last N days for a repo."""
    cutoff = datetime.now() - timedelta(days=days)
    t = con.table("raw_github_events")
    return (
        t.filter([
            t.repo_name == repo,
            t.type == "PullRequestEvent",
            t.created_at > cutoff,
        ])
        .agg(total_prs=t.id.count())
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_catalog_github.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/de_ecosystem/catalog/github.py tests/test_catalog_github.py
git commit -m "feat: catalog github expressions with grammar annotations"
```

---

## Task 8: Catalog — social (Bluesky) expressions

**Files:**
- Create: `src/de_ecosystem/catalog/social.py`
- Test: `tests/test_catalog_social.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_catalog_social.py
from de_ecosystem.catalog.social import social_buzz_score, trending_hashtags


def test_buzz_score_weights_engagement(con):
    df = social_buzz_score(con, "duckdb").execute()
    row = df.iloc[0]
    assert row["post_count"] >= 1
    # score = posts + likes*2 + reposts*3
    assert row["buzz_score"] == row["post_count"] + row["total_likes"] * 2 + row["total_reposts"] * 3


def test_trending_hashtags_returns_counts(con):
    df = trending_hashtags(con).execute()
    assert set(df.columns) == {"hashtag", "post_count"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_catalog_social.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `social.py`**

Copy verbatim from the reference repo's `catalog/social.py` (`social_buzz_score(con, keyword, days=7)` and `trending_hashtags(con, days=7, top_n=10)`). No changes.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_catalog_social.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/de_ecosystem/catalog/social.py tests/test_catalog_social.py
git commit -m "feat: catalog social (bluesky) expressions"
```

---

## Task 9: Catalog — composite (momentum) expressions

**Files:**
- Create: `src/de_ecosystem/catalog/composite.py`
- Test: `tests/test_catalog_composite.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_catalog_composite.py
from de_ecosystem.catalog.composite import ecosystem_health_score, rising_tools


def test_health_score_in_range(con):
    df = ecosystem_health_score(con, "dbt-core", "dbt-labs/dbt-core").execute()
    score = df["health_score"].iloc[0]
    assert 0.0 <= score <= 100.0


def test_rising_tools_ranks_descending(con):
    pairs = [("dbt-core", "dbt-labs/dbt-core"), ("polars", "pola-rs/polars")]
    df = rising_tools(con, pairs, top_n=5).execute()
    assert df["health_score"].is_monotonic_decreasing
    assert len(df) <= 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_catalog_composite.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `composite.py`**

Copy verbatim from the reference repo's `catalog/composite.py`. It defines `WEIGHTS`, `CEILINGS`, `CLOUD_REPOS`, `_safe_sum`, `ecosystem_health_score(con, tool, repo)`, `rising_tools(con, tool_repo_pairs, top_n=10)`, and `cloud_provider_momentum(con)`. No changes — the momentum weighting stays tunable (see plan note: revisit weights once real data is in front of us).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_catalog_composite.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/de_ecosystem/catalog/composite.py tests/test_catalog_composite.py
git commit -m "feat: catalog composite momentum expressions"
```

---

## Task 10: Ingest — dlt pipelines (RSS, Bluesky, PyPI, GitHub)

Ports the dlt ingestion. **Simplification:** drop the DEV/PROD split — keep only the local/DEV paths (pypistats REST, local gharchive glob). These are network-dependent, so they are smoke-tested for import + resource shape only (no live calls in CI).

**Files:**
- Create: `src/de_ecosystem/ingest/rss.py`
- Create: `src/de_ecosystem/ingest/bluesky.py`
- Create: `src/de_ecosystem/ingest/pypi.py`
- Create: `src/de_ecosystem/ingest/github.py`
- Test: `tests/test_ingest_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ingest_smoke.py
import duckdb


def test_ingest_modules_import():
    from de_ecosystem.ingest import rss, bluesky, pypi, github
    assert hasattr(rss, "run_rss_pipeline")
    assert hasattr(bluesky, "run_bluesky_pipeline")
    assert hasattr(pypi, "load_pypi")
    assert hasattr(github, "load_github")


def test_github_loader_handles_missing_files(tmp_path):
    from de_ecosystem.ingest.github import load_github_dev
    con = duckdb.connect(str(tmp_path / "t.duckdb"))
    load_github_dev(con, data_glob=str(tmp_path / "nope-*.json.gz"))
    # table is created even when no files match; stays empty
    rows = con.execute("SELECT count(*) FROM raw_github_events").fetchone()[0]
    assert rows == 0


def test_bluesky_hashtag_extraction():
    from de_ecosystem.ingest.bluesky import _extract_hashtags
    facets = [{"features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "duckdb"}]}]
    assert _extract_hashtags(facets) == ["duckdb"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ingest_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `rss.py` and `bluesky.py`**

Copy both verbatim from the reference repo (`ingest/rss.py`, `ingest/bluesky.py`). They already reference only `settings.db_path` and `settings.bsky_feed_uri`, both of which exist in the new `settings.py`. No changes.

- [ ] **Step 4: Create `pypi.py`** (DEV-only — remove the PROD/BigQuery function)

```python
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
```

- [ ] **Step 5: Create `github.py`** (DEV-only — remove the PROD/BigQuery function)

```python
import duckdb
from de_ecosystem.config import DE_REPOS
from de_ecosystem.settings import settings


def load_github_dev(
    con: duckdb.DuckDBPyConnection,
    data_glob: str | None = None,
    repos: list[str] | None = None,
) -> None:
    """Load GH Archive events from local NDJSON/JSON.gz files, filtered to DE repos."""
    data_glob = data_glob or settings.github_data_glob()
    repos = repos or DE_REPOS
    repo_list = ", ".join(f"'{r}'" for r in repos)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_github_events (
            id          TEXT PRIMARY KEY,
            created_at  TIMESTAMP,
            type        TEXT,
            repo_name   TEXT,
            actor_login TEXT
        )
    """)
    try:
        con.execute(f"""
            INSERT OR IGNORE INTO raw_github_events
            SELECT
                id,
                created_at::TIMESTAMP,
                type,
                repo.name   AS repo_name,
                actor.login AS actor_login
            FROM read_ndjson_auto('{data_glob}', ignore_errors := true)
            WHERE repo.name IN ({repo_list})
        """)
    except duckdb.IOException:
        pass  # no files found — table stays empty
    except Exception:
        pass


def load_github(db_path: str = settings.db_path) -> None:
    """Entry point: load GH Archive events into DuckDB."""
    con = duckdb.connect(db_path)
    load_github_dev(con)
    con.close()
```

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_ingest_smoke.py -v`
Expected: PASS (3 tests)

- [ ] **Step 7: Commit**

```bash
git add src/de_ecosystem/ingest tests/test_ingest_smoke.py
git commit -m "feat: dlt ingest pipelines (rss, bluesky, pypi, github), DEV-only"
```

---

## Task 11: Commit a tiny GitHub-events slice

The raw GH Archive hours are ~21MB each (425MB total) — far too big to commit. Filter them down to only DE-repo events into a single small `de-slice.json.gz` that `make ingest` reads.

**Files:**
- Create: `data/raw/gharchive/de-slice.json.gz` (small, force-added)
- Create: `scripts/make_gh_slice.py` (one-off generator, kept for reproducibility)

- [ ] **Step 1: Create `scripts/make_gh_slice.py`**

```python
"""Filter local GH Archive hours down to DE-repo events -> one small NDJSON.gz.

Reads from a source glob (default: the reference repo's downloaded hours) and
writes data/raw/gharchive/de-slice.json.gz with only rows whose repo.name is in
DE_REPOS. Run once to (re)generate the committed slice:

    uv run python scripts/make_gh_slice.py \
        --src '/home/sspaeti/Documents/work/xorq/de-ecosystem-digest/data/raw/gharchive/*.json.gz'
"""
import argparse
import duckdb
from de_ecosystem.config import DE_REPOS

OUT = "data/raw/gharchive/de-slice.json.gz"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="glob of source GH Archive .json.gz hours")
    args = ap.parse_args()

    repo_list = ", ".join(f"'{r}'" for r in DE_REPOS)
    con = duckdb.connect()
    con.execute(f"""
        COPY (
            SELECT *
            FROM read_ndjson_auto('{args.src}', ignore_errors := true)
            WHERE repo.name IN ({repo_list})
        ) TO '{OUT}' (FORMAT JSON, COMPRESSION GZIP)
    """)
    n = con.execute(
        f"SELECT count(*) FROM read_ndjson_auto('{OUT}', ignore_errors := true)"
    ).fetchone()[0]
    print(f"wrote {OUT} with {n} events")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Generate the slice from the reference repo's downloaded hours**

Run:
```bash
mkdir -p data/raw/gharchive
uv run python scripts/make_gh_slice.py \
  --src '/home/sspaeti/Documents/work/xorq/de-ecosystem-digest/data/raw/gharchive/*.json.gz'
```
Expected: prints `wrote data/raw/gharchive/de-slice.json.gz with <N> events` (N is small, on the order of tens to low hundreds). Verify the file is well under 1MB: `ls -lh data/raw/gharchive/de-slice.json.gz`.

- [ ] **Step 3: Verify the ingest loader reads the slice**

Run:
```bash
uv run python -c "from de_ecosystem.ingest.github import load_github; load_github()" && \
uv run python -c "import duckdb; print(duckdb.connect('de_ecosystem.duckdb').execute('select count(*) from raw_github_events').fetchone())"
```
Expected: a non-zero count matching (roughly) the slice's event count.

- [ ] **Step 4: Force-add the slice (it is gitignored by glob, allow-listed by name) and commit**

```bash
git add -f data/raw/gharchive/de-slice.json.gz
git add scripts/make_gh_slice.py
git commit -m "data: committed small DE-repo GH Archive slice + generator"
```

---

## Task 12: Catalog showcase entrypoint (`expr.py`)

Runs each named expression once — the "vocabulary" tour. Ported and trimmed (no prod, no BSL, no OmniGraph). Also exposes `star_velocity` as the named build target for `make manifest`.

**Files:**
- Create: `expr.py`
- Test: `tests/test_expr.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_expr.py
import subprocess
import sys


def test_expr_runs_without_error():
    # Runs against whatever de_ecosystem.duckdb exists (may be empty) — must not crash.
    result = subprocess.run(
        [sys.executable, "expr.py"],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stderr
    assert "Backend:" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_expr.py -v`
Expected: FAIL (no `expr.py` yet → non-zero return / `FileNotFoundError` in subprocess stderr)

- [ ] **Step 3: Create `expr.py`**

```python
"""xorq catalog entrypoint — runs every named expression from the catalog.

Run with: uv run python expr.py   (or: make catalog)
Also the build target for `xorq build expr.py -e star_velocity` (make manifest).
"""
from collections.abc import Callable

from de_ecosystem.settings import settings
from de_ecosystem.catalog.articles import tool_mention_frequency, source_output_rate
from de_ecosystem.catalog.pypi import download_trend_90d, adoption_acceleration, raw_download_volume
from de_ecosystem.catalog.github import star_velocity_30d, pr_merge_rate
from de_ecosystem.catalog.social import social_buzz_score, trending_hashtags
from de_ecosystem.catalog.composite import (
    ecosystem_health_score,
    rising_tools,
    cloud_provider_momentum,
)
from de_ecosystem.config import DE_TOOLS, DE_REPOS

DEMO_TOOL_REPO_PAIRS = list(zip(DE_TOOLS[:5], DE_REPOS[:5]))

con = settings.backend()
settings.load_tables_to_backend(con)

# Named build target for `xorq build expr.py -e star_velocity` (make manifest).
try:
    star_velocity = star_velocity_30d(con, "dbt-labs/dbt-core")
except Exception:
    star_velocity = None


def show(title: str, expr_fn: Callable) -> None:
    print(f"── {title} ──")
    try:
        df = expr_fn().execute()
        print(df.to_string() if not df.empty else "(no data)")
    except Exception as exc:
        print(f"(no data: {type(exc).__name__})")
    print()


def main() -> None:
    print(f"Backend: {settings.engine} | DB: {settings.db_path}\n")
    show("Articles: dbt mention frequency (30d)", lambda: tool_mention_frequency(con, "dbt"))
    show("Articles: source output rate", lambda: source_output_rate(con))
    show("PyPI: dbt-core download trend (90d)", lambda: download_trend_90d(con, "dbt-core").head())
    show("PyPI: dbt-core adoption acceleration", lambda: adoption_acceleration(con, "dbt-core"))
    show("PyPI: naive raw download volume (the pydantic trap)", lambda: raw_download_volume(con))
    show("GitHub: dbt-core star velocity (30d)", lambda: star_velocity_30d(con, "dbt-labs/dbt-core"))
    show("GitHub: dbt-core PR count (30d)", lambda: pr_merge_rate(con, "dbt-labs/dbt-core"))
    show("Social: DuckDB buzz score", lambda: social_buzz_score(con, "duckdb"))
    show("Social: trending hashtags (7d)", lambda: trending_hashtags(con))
    show("Composite: ecosystem health for dbt-core",
         lambda: ecosystem_health_score(con, "dbt-core", "dbt-labs/dbt-core"))
    show("Composite: rising tools top 5", lambda: rising_tools(con, DEMO_TOOL_REPO_PAIRS, top_n=5))
    show("Composite: cloud provider momentum", lambda: cloud_provider_momentum(con))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_expr.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add expr.py tests/test_expr.py
git commit -m "feat: catalog showcase entrypoint expr.py"
```

---

## Task 13: The headline — `digest.py` (momentum leaderboard + pydantic contrast)

The outcome the post leads with: two side-by-side tables — the naive raw-download leaderboard (pydantic on top) and the momentum leaderboard — plus the callout explaining why raw volume misleads.

**Files:**
- Create: `digest.py`
- Test: `tests/test_digest.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_digest.py
import pandas as pd
from de_ecosystem.catalog.composite import rising_tools
from de_ecosystem.catalog.pypi import raw_download_volume


def test_digest_builders_return_frames(con):
    from digest import build_momentum, build_naive
    momentum = build_momentum(con, [("dbt-core", "dbt-labs/dbt-core"), ("polars", "pola-rs/polars")])
    naive = build_naive(con)
    assert isinstance(momentum, pd.DataFrame) and "health_score" in momentum.columns
    assert isinstance(naive, pd.DataFrame) and "downloads" in naive.columns
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_digest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'digest'` (or ImportError for the functions)

- [ ] **Step 3: Create `digest.py`**

```python
"""THE headline: the Data Engineering ecosystem momentum digest.

Prints two leaderboards side by side:
  1. NAIVE — total PyPI downloads. pydantic wins, because it's a transitive
     dependency of half of PyData. Raw volume is the wrong signal.
  2. MOMENTUM — a composite of change/acceleration across PyPI trend, GitHub
     star velocity, Bluesky buzz, and blog mentions. This is the real digest.

Run with: uv run python digest.py   (or: make digest / make run-sentence)
"""
import pandas as pd

from de_ecosystem.settings import settings
from de_ecosystem.config import DE_TOOLS, DE_REPOS
from de_ecosystem.catalog.pypi import raw_download_volume
from de_ecosystem.catalog.composite import rising_tools

# Tool -> GitHub repo pairs used for the momentum ranking.
DIGEST_PAIRS = list(zip(DE_TOOLS, DE_REPOS[: len(DE_TOOLS)]))


def build_naive(con: object) -> pd.DataFrame:
    """The wrong leaderboard: rank by absolute PyPI download volume."""
    try:
        return raw_download_volume(con).execute().head(10).reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["package", "downloads"])


def build_momentum(con: object, pairs: list[tuple[str, str]]) -> pd.DataFrame:
    """The real leaderboard: rank by composite momentum score."""
    return rising_tools(con, pairs, top_n=10).execute()


def main() -> None:
    con = settings.backend()
    settings.load_tables_to_backend(con)

    naive = build_naive(con)
    momentum = build_momentum(con, DIGEST_PAIRS)

    print("=" * 64)
    print("  DE ECOSYSTEM DIGEST")
    print("=" * 64)
    print("\n── Naive leaderboard: raw PyPI downloads ──")
    print(naive.to_string(index=False) if not naive.empty else "(no data)")
    print(
        "\n  ^ pydantic tops this because half of PyData depends on it — a\n"
        "    transitive dependency, not a DE tool with momentum. Raw volume lies.\n"
    )
    print("── Momentum leaderboard: composite change/acceleration ──")
    print(momentum.to_string(index=False) if not momentum.empty else "(no data)")
    print()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_digest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add digest.py tests/test_digest.py
git commit -m "feat: digest.py — momentum leaderboard headline + pydantic contrast"
```

---

## Task 14: ML — fit-as-modifier, predict-as-verb

Port the ML pipeline; reframe docstrings around the grammar. Behaviour is unchanged from the reference repo.

**Files:**
- Create: `src/de_ecosystem/ml/splits.py`
- Create: `src/de_ecosystem/ml/features.py`
- Create: `src/de_ecosystem/ml/models.py`
- Test: `tests/test_ml.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ml.py
import pandas as pd
from de_ecosystem.ml.models import train_and_predict


def test_train_and_predict_returns_predictions(con):
    pairs = [
        ("dbt-core", "dbt-labs/dbt-core"),
        ("polars", "pola-rs/polars"),
        ("duckdb", "duckdb/duckdb"),
        ("dlt", "dlt-hub/dlt"),
    ]
    out = train_and_predict(con, pairs)
    assert isinstance(out, pd.DataFrame)
    assert "tool" in out.columns and "prediction" in out.columns
    assert len(out) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ml.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `splits.py` and `features.py`**

Copy both verbatim from the reference repo (`ml/splits.py` defines `make_splits`; `ml/features.py` defines `_safe_sum` and `build_feature_matrix`). No changes.

- [ ] **Step 4: Create `models.py`** (verbatim port; only the module docstring reframes the grammar)

Copy `ml/models.py` verbatim from the reference repo, and add this module docstring at the very top (above the imports):

```python
"""ML is not a separate dialect — it's the same four parts of speech.

  fit(...)     attaches a MODIFIER: the fitted model rides along as metadata
               (xorq tracks a training_hash) without changing what the
               expression computes — exactly Part 1's definition of a modifier
               ("this expression also represents a fitted model").
  predict(...) is a VERB: it returns an Ibis Table expression, so the whole
               train -> predict chain stays deferred, cacheable, and buildable
               with `xorq build` just like any metric.
"""
```

The rest of the file (`FEATURE_COLS`, `TARGET_COL`, `build_xorq_pipeline`, `train_and_predict`) is copied unchanged.

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_ml.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/de_ecosystem/ml tests/test_ml.py
git commit -m "feat: ML pipeline — fit-as-modifier, predict-as-verb"
```

---

## Task 15: Multi-engine runner (`engines.py`)

Runs the *same* `star_velocity` expression on DuckDB, DataFusion, and (guarded) Snowflake, printing per-engine results to show they match. Snowflake failures degrade to a clear skip message.

**Files:**
- Create: `engines.py`
- Test: `tests/test_engines.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_engines.py
def test_run_on_engine_matches_across_embedded():
    from engines import run_on_engine
    duck = run_on_engine("duckdb")
    fusion = run_on_engine("datafusion")
    # both embedded engines run the same expression on the same DuckDB source
    assert duck["ok"] is True and fusion["ok"] is True
    assert duck["total_stars"] == fusion["total_stars"]


def test_snowflake_skips_gracefully_without_creds(monkeypatch):
    from engines import run_on_engine
    # Force connect_env to fail -> must be caught and reported, not raised.
    import xorq.api as xo
    monkeypatch.setattr(xo.snowflake, "connect_env",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no creds")))
    result = run_on_engine("snowflake")
    assert result["ok"] is False and "skip" in result["note"].lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_engines.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engines'`

- [ ] **Step 3: Create `engines.py`**

```python
"""Execute anywhere: run the SAME star_velocity expression on multiple engines.

The transformation logic never changes — only which backend binds the noun and
crunches the Arrow. That's "define once, execute anywhere" from Part 1.

Run with: uv run python engines.py   (or: make engines)
"""
from de_ecosystem.settings import settings
from de_ecosystem.catalog.github import star_velocity_30d

REPO = "dbt-labs/dbt-core"
ENGINES = ["duckdb", "datafusion", "snowflake"]


def run_on_engine(engine: str, repo: str = REPO) -> dict:
    """Build + execute star_velocity on one engine. Returns a result/skip dict."""
    try:
        con = settings.backend(engine)
    except Exception as exc:
        return {"engine": engine, "ok": False, "note": f"skip — connect failed: {exc}"}
    try:
        settings.load_tables_to_backend(con)
        df = star_velocity_30d(con, repo).execute()
        total = int(df["stars"].sum()) if not df.empty else 0
        return {"engine": engine, "ok": True, "rows": len(df), "total_stars": total}
    except Exception as exc:
        return {"engine": engine, "ok": False, "note": f"skip — execute failed: {exc}"}


def main() -> None:
    print(f"Running star_velocity_30d('{REPO}') on each engine:\n")
    for engine in ENGINES:
        r = run_on_engine(engine)
        if r["ok"]:
            print(f"  {engine:11} ok   rows={r['rows']:>3}  total_stars={r['total_stars']}")
        else:
            print(f"  {engine:11} {r['note']}")
    print("\nSame expression, different engines — the grammar doesn't change.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_engines.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add engines.py tests/test_engines.py
git commit -m "feat: multi-engine runner (duckdb/datafusion/snowflake, guarded)"
```

---

## Task 16: Grammar demo module (`grammar.py`) for the pedagogical Makefile targets

Each function prints one part of speech so the Makefile targets have something concrete to run. Uses `star_velocity` throughout for a single coherent example.

**Files:**
- Create: `grammar.py`
- Test: `tests/test_grammar.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_grammar.py
import subprocess
import sys
import pytest


@pytest.mark.parametrize("part", ["noun", "verb", "template", "modifier", "run-sentence"])
def test_grammar_parts_run(part):
    result = subprocess.run(
        [sys.executable, "grammar.py", part],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stderr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_grammar.py -v`
Expected: FAIL (no `grammar.py`)

- [ ] **Step 3: Create `grammar.py`**

```python
"""The grammar of data, one part of speech at a time.

Usage: uv run python grammar.py <noun|verb|template|modifier|run-sentence>
Driven by the pedagogical Makefile targets (make noun, make verb, ...).
"""
import sys

from de_ecosystem.settings import settings
from de_ecosystem.catalog.github import star_velocity_30d

REPO = "dbt-labs/dbt-core"


def _con():
    con = settings.backend()
    settings.load_tables_to_backend(con)
    return con


def noun() -> None:
    """A source: a lazy pointer to data, no computation yet."""
    con = _con()
    t = con.table("raw_github_events")
    print("NOUN — a source, referenced but not acted on:\n")
    print("  con.table('raw_github_events')")
    print("\nSchema (known without reading any rows):\n")
    print(t.schema())


def verb() -> None:
    """Transforms applied to the noun — the expression is built but NOT executed."""
    con = _con()
    expr = star_velocity_30d(con, REPO)
    print("VERB — filter/mutate/group_by/agg/order_by compose a sentence.")
    print("The expression is fully built but unexecuted (deferred):\n")
    print(repr(expr))


def template() -> None:
    """The (con, repo) signature binds the same sentence to different nouns."""
    con = _con()
    print("TEMPLATE — one sentence, bound to many repos:\n")
    for repo in (REPO, "pola-rs/polars", "duckdb/duckdb"):
        rows = len(star_velocity_30d(con, repo).execute())
        print(f"  star_velocity_30d(con, '{repo}')  ->  {rows} week-rows")


def modifier() -> None:
    """A modifier rides alongside without changing what is computed — here, the engine binding."""
    print("MODIFIER — same expression, different engine binding:\n")
    for engine in ("datafusion", "duckdb"):
        con = settings.backend(engine)
        settings.load_tables_to_backend(con)
        total = int(star_velocity_30d(con, REPO).execute()["stars"].sum() or 0)
        print(f"  engine={engine:11}  total_stars={total}")
    print("\n(In ML, `fit` attaches another kind of modifier: 'this is a fitted model'.)")


def run_sentence() -> None:
    """Execute the full sentence end-to-end — the digest."""
    print("RUN-SENTENCE — say the whole thing out loud:\n")
    import digest
    digest.main()


DISPATCH = {
    "noun": noun,
    "verb": verb,
    "template": template,
    "modifier": modifier,
    "run-sentence": run_sentence,
}


def main() -> None:
    part = sys.argv[1] if len(sys.argv) > 1 else "run-sentence"
    fn = DISPATCH.get(part)
    if fn is None:
        print(f"unknown part: {part}; choose from {', '.join(DISPATCH)}")
        sys.exit(2)
    fn()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_grammar.py -v`
Expected: PASS (5 parametrized cases)

- [ ] **Step 5: Commit**

```bash
git add grammar.py tests/test_grammar.py
git commit -m "feat: grammar.py — noun/verb/template/modifier/run-sentence demos"
```

---

## Task 17: `scripts/summary.py` (ingest overview)

**Files:**
- Create: `scripts/summary.py`
- Test: covered by manual run (needs a populated DB); no unit test.

- [ ] **Step 1: Create `scripts/summary.py`**

Copy verbatim from `/home/sspaeti/Documents/work/xorq/de-ecosystem-digest/scripts/summary.py`. It reads `settings.db_path` read-only and prints row counts + `bar()` charts for articles/posts/github/pypi. It references only `settings.db_path`, which exists. No changes.

- [ ] **Step 2: Verify it runs against the DB built in Task 11**

Run: `uv run python scripts/summary.py`
Expected: prints "Row counts" and the four bar-chart sections (GitHub section populated from the slice; others may show `(no data)` until `make ingest` runs).

- [ ] **Step 3: Commit**

```bash
git add scripts/summary.py
git commit -m "feat: ingest summary script with bar charts"
```

---

## Task 18: Makefile (practical + grammar targets)

**Files:**
- Create: `Makefile`

- [ ] **Step 1: Create `Makefile`**

```makefile
.DEFAULT_GOAL := help

DB_PATH ?= de_ecosystem.duckdb

help: ## Show all targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync --extra dev

ingest: ## Run all dlt ingest pipelines into DuckDB (outside the grammar)
	uv run python -c "from de_ecosystem.ingest.rss import run_rss_pipeline; run_rss_pipeline()"
	uv run python -c "from de_ecosystem.ingest.bluesky import run_bluesky_pipeline; run_bluesky_pipeline()"
	uv run python -c "from de_ecosystem.ingest.pypi import load_pypi; load_pypi()"
	uv run python -c "from de_ecosystem.ingest.github import load_github; load_github()"

summary: ## Ingest overview with DuckDB bar() charts
	uv run python scripts/summary.py

catalog: ## Run every named catalog expression
	uv run python expr.py

digest: ## THE headline — momentum leaderboard + pydantic contrast
	uv run python digest.py

manifest: ## Compile star_velocity into a diffable xorq build artifact
	uv run xorq build expr.py -e star_velocity

engines: ## Run the same expression on DuckDB / DataFusion / Snowflake
	uv run python engines.py

ml: ## Train + predict tool adoption (fit=modifier, predict=verb)
	uv run python -c "from de_ecosystem.ml.models import train_and_predict; print(train_and_predict())"

test: ## Run the test suite (no network needed)
	uv run pytest tests/ -v

full-pipeline: ingest summary catalog digest manifest engines ml ## Run everything in order

clean: ## Archive the DB and reset dlt state to re-ingest from scratch
	mkdir -p archive
	@if [ -f $(DB_PATH) ]; then cp $(DB_PATH) archive/de_ecosystem_$$(date +%Y%m%d_%H%M%S).duckdb; echo "archived $(DB_PATH)"; fi
	rm -f $(DB_PATH) $(DB_PATH).wal
	rm -rf ~/.local/share/dlt/pipelines/rss_articles ~/.local/share/dlt/pipelines/bluesky_posts

# ── The grammar of data, as Makefile targets (map to the Part 2 sentence) ──
noun: ## 1. show the sources as lazy table pointers — no computation
	uv run python grammar.py noun

verb: ## 2. apply transforms; print the built (unexecuted) expression
	uv run python grammar.py verb

template: ## 3a. bind the schema-shaped expression to a repo
	uv run python grammar.py template

modifier: ## 3b. attach a modifier (engine binding / fitted-model)
	uv run python grammar.py modifier

run-sentence: ## 5. execute the full sentence end-to-end → the digest
	uv run python grammar.py run-sentence
```

- [ ] **Step 2: Verify the grammar targets run end-to-end**

Run: `make noun && make verb && make template && make modifier && make run-sentence`
Expected: each prints its section without error (GitHub-backed since the slice is ingested).

- [ ] **Step 3: Verify `make test` passes**

Run: `make test`
Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git add Makefile
git commit -m "feat: Makefile — practical + grammar-of-data targets"
```

---

## Task 19: Manifest artifact (commit one build for the PR-diff demo)

`builds/` is gitignored; force-add exactly one artifact so the `git diff` of `expr.yaml` is reproducible from the repo.

**Files:**
- Create: `builds/<hash>/...` (generated by `xorq build`, one artifact force-added)

- [ ] **Step 1: Build the manifest**

Run: `make manifest`
Expected: prints a build hash and writes `builds/<hash>/` containing `expr.yaml` (plus `deferred_reads.yaml`, `sql.yaml`, `metadata.json`, `requirements.txt` per xorq's build output).

- [ ] **Step 2: Inspect the artifact is diffable**

Run: `ls builds/ && find builds -name expr.yaml`
Expected: one build directory; `expr.yaml` exists and is human-readable YAML.

- [ ] **Step 3: Force-add the single artifact and commit**

```bash
git add -f builds/
git commit -m "build: commit one star_velocity manifest for the PR-diff demo"
```

Note for the post: change `days=30`→`90` in `catalog/github.py`, re-run `make manifest`, and `git diff builds/*/expr.yaml` shows the semantic change reviewable in a PR.

---

## Task 20: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
# DE Ecosystem Digest (simple)

A minimal [xorq](https://github.com/xorq-labs/xorq) project that builds a **Data
Engineering ecosystem momentum digest** from four public signals — and uses it to
demonstrate the *grammar of data* (noun → verb → template → modifier → manifest →
execute) from [Part 1](https://xorq.dev/blog/grammar-for-data-engineering/).

## The digest, first

```bash
make install
make ingest     # dlt → de_ecosystem.duckdb (RSS, Bluesky, PyPI, GitHub)
make digest     # the momentum leaderboard (+ why raw downloads mislead)
```

Raw PyPI downloads put **pydantic** on top — because half of PyData depends on it,
not because it has momentum. The digest instead ranks by a composite of
change/acceleration (PyPI trend, GitHub star velocity, Bluesky buzz, blog mentions).

## The grammar, as Makefile targets

```bash
make noun          # sources as lazy pointers — no computation
make verb          # transforms compose an unexecuted expression
make template      # bind the sentence to any repo
make modifier      # same expression, different engine binding
make manifest      # compile to a diffable expr.yaml — model once
make run-sentence  # execute end-to-end → the digest
```

`star_velocity_30d` in `src/de_ecosystem/catalog/github.py` labels every part of
speech inline.

## Execute anywhere

```bash
make engines   # same star_velocity on DuckDB, DataFusion, and Snowflake
```

Snowflake reads `SNOWFLAKE_*` from `.env`; it skips with a clear message if
unreachable.

## Where the grammar stops (and how to extend it)

- **Ingestion is outside the grammar.** dlt handles extraction (imperative,
  stateful) into DuckDB — the boundary is deliberate. Swap in incremental loads or
  more sources without touching the catalog.
- **Metrics live in the catalog as plain xorq expressions.** To grow them into a
  full metrics layer, lift the composite definitions into the
  [boring-semantic-layer](https://github.com/boringdata/boring-semantic-layer)
  (dimensions/measures over the same xorq tables). Sketch:

  ```python
  # from boring_semantic_layer import SemanticModel, Measure, Dimension
  # downloads = Measure("sum", "downloads"); tool = Dimension("package")
  # ... query momentum by tool, this week — same tables, richer surface.
  ```

- **ML is not a separate dialect.** `fit` attaches a *modifier* (the fitted model),
  `predict` is a *verb* returning a Table expression — so inference is buildable
  with `xorq build` just like a metric. See `src/de_ecosystem/ml/models.py`.

## Project layout

```
digest.py            # headline momentum leaderboard
expr.py              # catalog showcase (build target for manifest)
engines.py           # multi-engine runner
grammar.py           # noun/verb/template/modifier/run-sentence demos
src/de_ecosystem/
  settings.py        # engine switch + DuckDB→backend bridge
  config.py          # feeds, repos, tools
  ingest/            # dlt: rss, bluesky, pypi, github (outside the grammar)
  catalog/           # xorq expressions: articles, pypi, github, social, composite
  ml/                # splits, features, models
scripts/summary.py   # ingest overview
data/raw/gharchive/  # small committed GH-repo slice
```

Run `make test` for the offline test suite.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with digest quickstart, grammar targets, BSL on-ramp"
```

---

## Task 21: Full verification pass

- [ ] **Step 1: Run the whole test suite**

Run: `make test`
Expected: every test PASSES.

- [ ] **Step 2: Run the full pipeline end-to-end**

Run: `make full-pipeline`
Expected: ingest → summary → catalog → digest → manifest → engines → ml all complete without error (Snowflake may print a skip line if creds are absent; that is acceptable).

- [ ] **Step 3: Confirm the digest output is real**

Run: `make digest`
Expected: the naive leaderboard shows pydantic at/near the top; the momentum leaderboard shows a defensible ranking. **Capture this output** — the two most interesting findings from it feed the blog section (Task 22).

- [ ] **Step 4: Commit any fixups**

```bash
git add -A && git commit -m "chore: full-pipeline verification fixups" || echo "nothing to fix"
```

---

## Task 22: Final deliverable — blog section "The Grammar of Data, in Action"

Only after the pipeline runs and the digest output is captured. Write the section into the draft using real code/output from this project.

**Files:**
- Modify: `/home/sspaeti/Simon/SecondBrain/⚛️ Areas/⚖️ SSP Data/Clients/content-gh/ssp-data/writing-xorq/Grammar for DE (Part 2) - xorq.md`

- [ ] **Step 1: Draft the section**

Under the existing `## The Grammar of Data, in Action` heading, write the noun/verb/template+modifier/manifest/execute sentence for THIS project, using the real `star_velocity_30d` code and the `make digest` output captured in Task 21. Include the extensibility note: full lineage, deterministic reruns, metrics in the catalog, and per-stage extension points (catalog → boring-semantic-layer; dlt for incremental ingestion into a staging area). Pick the two most interesting real findings for the opener (per the design's data-driven narrative).

- [ ] **Step 2: Prefix every added line with `#CLAUDE:`**

Every line you add to the markdown file must be prefixed with `#CLAUDE:` so authorship is unambiguous, per the user's instruction.

- [ ] **Step 3: Show the user the diff and stop**

Do not commit the blog file (it lives in a separate vault, not this repo). Present the added section to the user for review.

---

## Self-Review (completed while writing)

**Spec coverage:** every spec section maps to a task — narrative/pydantic callout (Tasks 6, 13, 22); dlt ingest outside grammar (Task 10); 4 sources (Tasks 5–8, 10, 11); catalog with star_velocity anchor (Task 7); momentum digest (Tasks 9, 13); manifest demo (Tasks 12, 19); multi-engine DuckDB/DataFusion/Snowflake (Tasks 3, 15); ML-as-modifier (Task 14); grammar Makefile targets (Tasks 16, 18); BSL on-ramp note (Task 20); engine-switch settings, no DEV/PROD (Task 3); removed OmniGraph/semantic/BigQuery (absent by construction); offline tests (Task 4 + per-task tests); blog section (Task 22).

**Placeholder scan:** no TBD/TODO left in code steps; every code step contains full content. The only deferred decisions (exact momentum weights, the two headline findings) are intentionally data-driven and are resolved in Tasks 21–22 against real output, matching the spec's "Open questions."

**Type consistency:** `settings.backend(engine)` / `load_tables_to_backend(con)` signatures are consistent across Tasks 3, 12, 13, 15, 16; catalog function names (`star_velocity_30d`, `rising_tools`, `raw_download_volume`) match every call site; `run_on_engine` returns a dict with `ok`/`total_stars` used consistently in Task 15's tests.
```

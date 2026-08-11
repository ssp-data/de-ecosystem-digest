# De Ecosystem Digest (Simple) — Design Spec

**Date:** 2026-08-11
**Status:** Approved design, ready for implementation planning
**Companion to:** [The Grammar of Data Engineering — Part 1](https://xorq.dev/blog/grammar-for-data-engineering/) and the Part 2 draft (`Grammar for DE (Part 2) - xorq.md`)

## Purpose

A deliberately small, readable xorq project that demonstrates the **grammar of data** from Part 1 in action, by building a **Data Engineering Ecosystem Digest**: a ranked "momentum" leaderboard of DE tools built from four public signals.

This is a fresh, simplified rebuild of the existing `de-ecosystem-digest` project. The original grew too complex (OmniGraph knowledge graph, boring-semantic-layer wiring, DEV/PROD BigQuery+MotherDuck switching). This version keeps only what teaches the grammar and produces a compelling outcome.

**Lead with the outcome, then decompose it into the grammar.** The reader first sees the digest, then learns how noun → verb → template → modifier → manifest → execute produced it.

## Non-goals (explicitly removed)

- **OmniGraph / knowledge graph** (`knowledge/`, `make ask`, `make knowledge`) — gone entirely.
- **boring-semantic-layer wiring** (`semantic/`) — replaced by a short "extend with BSL" note + a commented code path in the README. Metrics stay as plain xorq `catalog/` expressions.
- **DEV/PROD source switching** (`DE_ENV=dev/prod`, BigQuery public data, MotherDuck, `make fetch-gharchive`) — removed. GH Archive slice is committed to the repo.

## Narrative arc (how the post reads)

The findings are **data-driven** — discovered from real output, not pre-written. The opener stays a placeholder until we run the digest and pick the two most interesting real stories.

1. **Here's the digest** — the momentum leaderboard drops (headline findings TBD from real data).
2. **The naive version is wrong** — sorting by raw PyPI downloads puts pydantic on top (~5.0B) because it's a transitive dependency of half of PyData, not a DE tool with momentum. This is a *structural* callout (the mechanism), not a "finding."
3. **The grammar fixes it** — the composite momentum expression, with noun / verb / template / modifier labeled inline in the code.
4. **Manifest it** — `star_velocity` → `expr.yaml`; change `days=30`→`90` and show the diff in a PR. *Model once.*
5. **Execute anywhere** — the same expression on DuckDB, DataFusion, and Snowflake.
6. **ML is not a separate dialect** — a fitted model is a **modifier**, `predict` is a **verb**. The four parts of speech already cover ML.

## Architecture

Ingestion (dlt, imperative, **outside** the grammar) writes raw tables to a local DuckDB file. The xorq catalog (declarative, **the grammar**) reads them and produces named, executable, manifestable expressions.

```
┌─ Ingest (dlt — outside grammar) ─┐   ┌─ Catalog (xorq — the grammar) ──────┐
│ dlt → RSS articles               │   │ named Ibis/xorq expressions          │
│ dlt → Bluesky posts              │ → │ articles / pypi / github / social    │
│ dlt → PyPI downloads             │   │ composite → momentum leaderboard     │
│ dlt → GitHub events (committed)  │   │ ML pipeline (fit = modifier)         │
└─ DuckDB (de_ecosystem.duckdb) ───┘   └─ execute on DuckDB/DataFusion/SF ────┘
```

The boundary is deliberate and stated in the post: extraction is imperative, stateful, engine-specific — dlt owns it. The grammar covers transformation and inference.

## Project structure

```
de-ecosystem-digest-simple/
├── digest.py              # THE headline entrypoint → prints the momentum leaderboard
├── expr.py                # catalog showcase → runs each named expression
├── src/de_ecosystem/
│   ├── settings.py        # backend(engine=duckdb|datafusion|snowflake) + dlt→duckdb bridge
│   ├── config.py          # DE_FEEDS, DE_REPOS, DE_TOOLS
│   ├── ingest/            # dlt: rss, bluesky, pypi, github   (outside the grammar)
│   ├── catalog/           # xorq expressions: articles, pypi, github, social, composite
│   └── ml/                # splits, features, models
├── scripts/summary.py     # ingest overview (bar charts)
├── data/raw/gharchive/    # small committed GH Archive slice
├── builds/                # one un-ignored manifest artifact for the PR-diff demo
├── Makefile · README.md · .env(.example)
```

Carried over from the original repo (simplified): `config.py`, `ingest/`, `catalog/`, `ml/`, `scripts/summary.py`. Rewritten: `settings.py` (engine switching instead of DEV/PROD). New: `digest.py`, grammar Makefile targets.

## Components

### Sources & ingestion (dlt — kept)

Four sources, ingested by dlt into `de_ecosystem.duckdb`:

| Source | Table | Notes |
|---|---|---|
| RSS (~64 DE blogs, `config.py`) | `articles` | feedparser via dlt |
| Bluesky DE feed | `posts` | AT Protocol via dlt |
| PyPI downloads | `raw_pypi_downloads` | pypistats.org REST via dlt |
| GitHub events | `raw_github_events` | committed `data/raw/gharchive/*.json.gz` |

Ingestion stays idempotent (dlt merge on id). The post's one line: "dlt handles ingestion — outside the grammar; that boundary is deliberate."

### Catalog — the grammar in code

Keep the existing named expressions: `tool_mention_frequency`, `source_output_rate` (articles); `download_trend_90d`, `adoption_acceleration` (pypi); `star_velocity_30d`, `pr_merge_rate` (github); `social_buzz_score`, `trending_hashtags` (social); `ecosystem_health_score`, `rising_tools`, `cloud_provider_momentum` (composite).

`star_velocity_30d` is the **pedagogical anchor** — parts of speech labeled inline:

- **noun** — `con.table("raw_github_events")` (a lazy pointer, no computation)
- **verbs** — `.filter → .mutate → .group_by → .agg → .order_by`
- **template** — the signature `star_velocity_30d(con, repo)`; the same sentence binds to any repo
- **modifier** — the backend binding (which engine executes it)

### Headline output — momentum leaderboard (`digest.py`)

Prints the ranked digest table. **Momentum** = a weighted blend of change/acceleration signals (PyPI trend %, star velocity, Bluesky buzz, blog mention rate) — explicitly **not** absolute volume. Alongside it, a second "naive raw-downloads" table so the pydantic callout is visible side-by-side. Momentum reuses the existing composite expressions (`rising_tools` / `ecosystem_health_score`), refined so the ranking is defensible.

### Manifest demo

`make manifest` → `xorq build expr.py -e star_velocity` → `builds/<hash>/expr.yaml`. One artifact is un-ignored (committed) so the reader can reproduce the `days=30`→`90` `git diff` of `expr.yaml`. This is the Write → Manifest → Execute cycle made tangible.

### Multi-engine execution

`make engines` (or `make run-sentence` on a chosen engine) runs the *same* `star_velocity` expression on:

- **DuckDB** — `xo.duckdb.connect()`
- **DataFusion** — `xo.connect()` (default embedded)
- **Snowflake** — `xo.snowflake.connect()` from `.env` (`SNOWFLAKE_*`)

Prints per-engine results to show they match. **Snowflake is guarded**: if creds are missing or the connection fails, it prints a clear "skipping Snowflake" message and continues — the demo never hard-fails on network.

### ML — a modifier, not a separate section

Keep `ml/` minimal and reframe around the grammar:

- `train_test_splits` — deterministic hashing expressed as an expression (same seed → same rows, no pickled state).
- `fit` — **attaches a modifier**: the fitted model rides along as metadata (`training_hash`) without changing what the expression computes. This matches Part 1's exact definition of a modifier ("this expression also represents a fitted model").
- `predict` — a **verb**: returns an Ibis Table expression.
- Payoff: because `predict` is an expression, `xorq build` manifests the inference pipeline too. Deploying a model collapses into the same Write → Manifest → Execute cycle.

### Makefile

**Practical targets:** `install · ingest · summary · catalog · digest · manifest · engines · ml · test · full-pipeline · clean`

**Grammar targets** (the Makefile *becomes* the grammar — pedagogical, map to the Part 2 sentence steps):

```
make noun          # 1. show the sources as lazy table pointers — no computation
make verb          # 2. apply transforms; print the built (unexecuted) expression
make template      # 3a. bind the schema-shaped expression to a repo/tool
make modifier      # 3b. attach a modifier (fitted-model / backend binding)
make manifest      # 4. compile to expr.yaml — model once, diffable artifact
make run-sentence  # 5. execute the full sentence end-to-end → the digest
```

`make run-sentence` is the payoff — the whole grammar of data, run.

## Settings design (engine switching)

`settings.backend(engine: "duckdb" | "datafusion" | "snowflake")` returns the chosen xorq backend. `load_tables_to_backend(con)` bridges the dlt-written DuckDB tables into the chosen backend (copy for embedded engines; load into a scratch schema for Snowflake). No `DE_ENV`; engine is the only switch and defaults to DataFusion.

## Error handling

- Missing/empty raw tables → catalog expressions print `(no data)` rather than crashing (as the current `expr.py` already does).
- Snowflake unreachable → guarded skip with a clear message.
- `make clean` archives the DuckDB file and resets dlt state to re-ingest from scratch.

## Testing

`make test` → pytest, no network required. Tests run catalog expressions against a small committed fixture DuckDB (or the committed gharchive slice + tiny seeded tables) and assert expression shapes/types — including that `predict` returns a Table expression and that the same expression executes on DuckDB and DataFusion with matching results.

## Final deliverable — blog section

After the project is built and the digest has been run on real data, write the **"The Grammar of Data, in Action"** section into:

`/home/sspaeti/Simon/SecondBrain/⚛️ Areas/⚖️ SSP Data/Clients/content-gh/ssp-data/writing-xorq/Grammar for DE (Part 2) - xorq.md`

Every added line prefixed `#CLAUDE:` so authorship is clear. The section fills in the noun/verb/template+modifier/manifest/execute sentence using the real code, plus the extensibility note: full lineage, deterministic reruns, metrics in the catalog, and per-stage extension points (catalog → BSL; dlt for incremental ingestion into a staging area).

## Open questions / to refine during implementation

- Exact momentum weighting — tune once real data is in front of us so the top ranks are defensible.
- Which two headline findings lead the post — chosen from real output, not now.
- Whether Snowflake needs a one-time table load step or can read via `into_backend` — decide against the live account during implementation.

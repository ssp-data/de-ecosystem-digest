# DE Ecosystem Digest (simple)

A minimal [xorq](https://github.com/xorq-labs/xorq) project that builds a **Data
Engineering ecosystem momentum digest** from four public signals — and uses it to
demonstrate the *grammar of data* (noun → verb → template → modifier → manifest →
execute) from [Part 1](https://xorq.dev/blog/grammar-for-data-engineering/).

## What it does

Which data engineering tools are actually gaining momentum — not which have the
biggest install base? Star counts and total downloads reward incumbents and
transitive dependencies; they don't tell you what the community is *moving toward*
right now. This project pulls four public signals about the DE ecosystem and lets
you rank tools by **change** (growth, velocity, buzz) instead of absolute size —
so a fast-rising newcomer can outrank a large-but-flat incumbent.

## The data

All four sources are ingested with [dlt](https://dlthub.com) into a local DuckDB
file (`make ingest`). Each is a different angle on the same question — what's the DE
ecosystem paying attention to?

| Source | What we pull | What you can analyze |
|--------|--------------|----------------------|
| **[Data Engineering RSS feeds](https://www.ssp.sh/brain/rss-feeds-for-data-engineering)** | Posts from ~90 vendor + community DE blogs | What people are *writing about* — tool mentions, publishing rate per source |
| **Bluesky posts** | Recent posts matching each tool's keyword | Social buzz — what people are *talking about*, trending hashtags |
| **PyPI downloads** | Daily download counts per package | Adoption *trend* — 90-day growth %, acceleration, not just raw volume |
| **GitHub Archive events** | Push / PR / star events from the GH event firehose | Developer *activity* — star velocity, PR merge rate |

Once ingested, the tables are yours to query directly, or via the curated
expressions in `src/de_ecosystem/catalog/` (articles, pypi, github, social,
composite) that the digest is built from.

## The digest, first

```bash
make install
make ingest     # dlt → de_ecosystem.duckdb (RSS, Bluesky, PyPI, GitHub)
make digest     # the momentum leaderboard (+ why raw downloads mislead)
```

Raw PyPI downloads put **pydantic** on top — because half of PyData depends on it,
not because it has momentum. The digest instead ranks by a composite of
change/acceleration (PyPI trend, GitHub star velocity, Bluesky buzz, blog mentions).

## Declarative stack

The whole pipeline — engine, sources, and the momentum metric — is described in one
readable file, [`stack.yaml`](stack.yaml). Swap `engine: duckdb` there and the
digest re-binds; adjust `momentum.window_days` and the leaderboard follows.
Precedence is **environment variable > `stack.yaml` > built-in default**, so the
YAML is the source of truth while env vars (`DE_ENGINE`, `DE_WINDOW_DAYS`,
`DE_BSKY_MAX_PAGES`, …) still override for one-off runs.

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

## Make targets → xorq, by grammar part

| make target      | xorq / Python call                         | grammar part            |
|------------------|--------------------------------------------|-------------------------|
| `make noun`      | `con.table(...)`                           | noun (source)           |
| `make verb`      | `.filter/.mutate/.agg` (deferred expr)     | verbs (transform)       |
| `make template`  | `star_velocity_30d(con, repo)`             | template (bind by arg)  |
| `make modifier`  | `settings.backend(engine)`                 | modifier (engine/fit)   |
| `make lineage`   | `expr.op()` / `ibis.to_sql` / `expr.ls`    | lineage (what xorq sees)|
| `make manifest`  | `xorq build expr.py -e star_velocity`      | model once → expr.yaml  |
| `make run-sentence` | `digest.main()` → `.execute()`          | execute the sentence    |
| `make engines`   | `settings.backend(x)` + `expr.execute()`   | represent everywhere    |

## Execute anywhere

```bash
make engines   # same star_velocity on DuckDB, DataFusion, and Snowflake
```

Snowflake reads `SNOWFLAKE_*` from `.env`; it skips with a clear message if
unreachable.

## The catalog: versioned, executable entries

`make catalog` registers a curated set of expressions as **versioned entries** in a local,
git-backed catalog at `./catalog` — the real [`xorq catalog`](https://docs.xorq.dev/api_reference/cli/index.html#catalog),
not just naming. Each entry is content-addressed; xorq bundles the source read at build time, so
entries are **reproducible without re-running ingest**. Editing an expression changes its hash →
a new versioned entry (the old one stays retrievable).

```bash
make preview                          # execute every named expression (dev overview)
make catalog                          # register curated entries → ./catalog
make catalog-list                     # entries (kind) + aliases
make catalog-run ALIAS=dbt-momentum   # execute an entry — reproducible, no ingest
cd catalog && git log --oneline       # one commit per entry = version history
```

Curated aliases: `dbt-star-velocity`, `dbt-download-trend`, `dbt-momentum`, `duckdb-buzz`,
`dbt-mentions`, `dbt-health`, `rising-tools` (see `CATALOG_ENTRIES` in `expr.py`).

## Where the grammar stops (and how to extend it)

- **Ingestion is outside the grammar.** dlt handles extraction (imperative,
  stateful) into DuckDB — the boundary is deliberate. Swap in incremental loads or
  more sources without touching the catalog.
- **Metrics live in the catalog as plain xorq expressions** — and `make catalog`
  registers them as versioned, content-addressed entries (see above). To grow them
  into a full metrics layer, lift the composite definitions into the
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
expr.py              # named expressions + curated CATALOG_ENTRIES (build/register target)
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

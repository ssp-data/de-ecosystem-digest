.DEFAULT_GOAL := help
# Targets are commands, not files — needed since ./catalog is also a directory.
.PHONY: help install ingest summary preview catalog catalog-list catalog-run digest \
        manifest engines ml test full-pipeline clean noun verb template modifier \
        lineage run-sentence

DB_PATH ?= de_ecosystem.duckdb
CATALOG ?= ./catalog

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

preview: ## Run every named expression and print result tables (dev overview)
	uv run python expr.py

catalog: ## Register curated expressions as versioned entries in ./catalog (real xorq catalog)
	uv run python scripts/catalog_register.py
	uv run xorq catalog --path $(CATALOG) list --kind

catalog-list: ## List catalog entries (kind) and their aliases
	uv run xorq catalog --path $(CATALOG) list --kind
	@echo "--- aliases ---"
	uv run xorq catalog --path $(CATALOG) list-aliases

catalog-run: ## Execute a catalog entry — reproducible, no ingest (ALIAS=dbt-momentum)
	uv run xorq catalog --path $(CATALOG) run $(or $(ALIAS),dbt-momentum) -o - -f csv

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

full-pipeline: ingest summary preview catalog digest manifest engines ml ## Run everything in order

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

lineage: ## show xorq lineage of star_velocity (sources, SQL, engine) — no data run
	uv run python grammar.py lineage

run-sentence: ## 5. execute the full sentence end-to-end → the digest
	uv run python grammar.py run-sentence

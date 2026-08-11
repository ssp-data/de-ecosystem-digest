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

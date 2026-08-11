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
    except ModuleNotFoundError:
        return {"engine": engine, "ok": False,
                "note": "skip — Snowflake driver missing (run: uv sync)"}
    except KeyError as exc:
        var = exc.args[0] if exc.args else "a credential"
        return {"engine": engine, "ok": False,
                "note": f"skip — {var} not set (export it in your shell, or add it to .env)"}
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

"""
Ingest summary — row counts and bar() charts straight from DuckDB.

Run with: make summary
"""
import duckdb

from de_ecosystem.settings import settings


def _columns(con: duckdb.DuckDBPyConnection, table: str) -> set[str]:
    rows = con.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = ?",
        [table],
    ).fetchall()
    return {r[0] for r in rows}


def show(con: duckdb.DuckDBPyConnection, title: str, sql: str) -> None:
    print(f"── {title} ──")
    try:
        df = con.execute(sql).df()
        print(df.to_string(index=False) if not df.empty else "(no data)")
    except Exception as exc:
        print(f"(no data: {exc})")
    print()


def main() -> None:
    con = duckdb.connect(settings.db_path, read_only=True)

    show(con, "Row counts", """
        SELECT 'articles' AS "table", count(*) AS rows FROM articles
        UNION ALL SELECT 'posts', count(*) FROM posts
        UNION ALL SELECT 'raw_pypi_downloads', count(*) FROM raw_pypi_downloads
        UNION ALL SELECT 'raw_github_events', count(*) FROM raw_github_events
    """)

    show(con, "Articles per source (top 15)", """
        WITH source_data AS (
            SELECT source_name, count(*) AS articles
            FROM articles GROUP BY source_name
        )
        SELECT source_name, articles,
               bar(articles, 0, (SELECT max(articles) FROM source_data), 30) AS chart
        FROM source_data ORDER BY articles DESC LIMIT 15
    """)

    quotes = "sum(quotes)" if "quotes" in _columns(con, "posts") else "0"
    show(con, "Bluesky engagement by author (top 15)", f"""
        WITH engagement_data AS (
            SELECT author_handle,
                   count(*)         AS posts,
                   sum(reply_count) AS replies,
                   sum(reposts)     AS reposts,
                   sum(likes)       AS likes,
                   {quotes}         AS quotes,
                   sum(likes + reposts + reply_count) AS total_engagement
            FROM posts GROUP BY author_handle
        )
        SELECT author_handle, posts, replies, reposts, likes, quotes,
               bar(total_engagement, 0,
                   (SELECT max(total_engagement) FROM engagement_data),
                   30) AS engagement_chart
        FROM engagement_data ORDER BY total_engagement DESC LIMIT 15
    """)

    show(con, "GitHub events by repo (top 15)", """
        WITH repo_data AS (
            SELECT repo_name, count(*) AS events
            FROM raw_github_events GROUP BY repo_name
        )
        SELECT repo_name, events,
               bar(events, 0, (SELECT max(events) FROM repo_data), 30) AS chart
        FROM repo_data ORDER BY events DESC LIMIT 15
    """)

    show(con, "PyPI downloads by package (sum of last ~180 days, without mirrors)", """
        WITH pkg_data AS (
            SELECT package, sum(downloads) AS downloads
            FROM raw_pypi_downloads
            WHERE category = 'without_mirrors'
            GROUP BY package
        )
        SELECT package, downloads,
               bar(downloads, 0, (SELECT max(downloads) FROM pkg_data), 30) AS chart
        FROM pkg_data ORDER BY downloads DESC
    """)

    con.close()


if __name__ == "__main__":
    main()

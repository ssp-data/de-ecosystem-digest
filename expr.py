"""xorq catalog entrypoint — runs every named expression from the catalog.

Run with: uv run python expr.py   (or: make catalog)
Also the build target for `xorq build expr.py -e star_velocity` (make manifest).
"""
from collections.abc import Callable

from de_ecosystem.settings import settings
from de_ecosystem.catalog.articles import tool_mention_frequency, source_output_rate
from de_ecosystem.catalog.pypi import download_trend_90d, adoption_acceleration, raw_download_volume, download_momentum
from de_ecosystem.catalog.github import star_velocity_30d, pr_merge_rate
from de_ecosystem.catalog.social import social_buzz_score, trending_hashtags
from de_ecosystem.catalog.composite import (
    ecosystem_health_score,
    rising_tools,
    cloud_provider_momentum,
)
from de_ecosystem.config import DE_TOOLS, DE_REPOS, TOOL_REPOS

DEMO_TOOL_REPO_PAIRS = list(TOOL_REPOS.items())[:5]

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
    show("PyPI: dbt-core 90d momentum", lambda: download_momentum(con, "dbt-core"))
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

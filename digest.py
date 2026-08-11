"""THE headline: the Data Engineering ecosystem momentum digest.

Prints two leaderboards:
  1. NAIVE — total PyPI downloads. pydantic wins because it's a transitive
     dependency of half of PyData. Raw volume is the wrong signal.
  2. MOMENTUM — 90-day PyPI download growth %, with each tool's Bluesky buzz
     alongside. Change and social signal, not absolute volume.

Run with: uv run python digest.py   (or: make digest / make run-sentence)
"""
import pandas as pd

from de_ecosystem.settings import settings
from de_ecosystem.stack import stack
from de_ecosystem.config import DE_TOOLS, TOOL_KEYWORDS
from de_ecosystem.catalog.pypi import raw_download_volume, download_momentum
from de_ecosystem.catalog.social import social_buzz_score

WINDOW_DAYS = stack.window_days


def build_naive(con: object) -> pd.DataFrame:
    """The wrong leaderboard: rank by absolute PyPI download volume."""
    try:
        return raw_download_volume(con).execute().head(10).reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["package", "downloads"])


def _buzz(con: object, tool: str) -> int:
    """All-time Bluesky buzz score for a tool's keyword (0 on any failure)."""
    keyword = TOOL_KEYWORDS.get(tool, tool)
    try:
        return int(social_buzz_score(con, keyword, days=3650).execute()["buzz_score"].iloc[0])
    except Exception:
        return 0


def build_momentum(con: object, tools: list[str], window_days: int = WINDOW_DAYS) -> pd.DataFrame:
    """The real leaderboard: rank tools by PyPI growth %, with Bluesky buzz alongside."""
    rows = []
    for tool in tools:
        try:
            row = download_momentum(con, tool, window_days).execute().iloc[0].to_dict()
        except Exception:
            continue
        row["buzz"] = _buzz(con, tool)
        rows.append(row)
    if not rows:
        return pd.DataFrame(columns=["package", "growth_pct", "recent_daily", "total_downloads", "buzz"])
    return pd.DataFrame(rows).sort_values("growth_pct", ascending=False).reset_index(drop=True)


def main() -> None:
    con = settings.backend()
    settings.load_tables_to_backend(con)

    naive = build_naive(con)
    momentum = build_momentum(con, stack.tools, WINDOW_DAYS)

    print("=" * 72)
    print("  DE ECOSYSTEM DIGEST")
    print("=" * 72)
    print("\n── Naive leaderboard: raw PyPI downloads (all-time) ──")
    print(naive.to_string(index=False) if not naive.empty else "(no data)")
    print(
        "\n"
    )
    print(f"── Momentum leaderboard: {WINDOW_DAYS}d download growth % + Bluesky buzz ──")
    print(momentum.to_string(index=False) if not momentum.empty else "(no data)")

if __name__ == "__main__":
    main()

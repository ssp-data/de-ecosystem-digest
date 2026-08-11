import pandas as pd
import xorq.api as xo
from de_ecosystem.catalog.github import star_velocity_30d
from de_ecosystem.catalog.pypi import download_trend_90d
from de_ecosystem.catalog.articles import tool_mention_frequency
from de_ecosystem.catalog.social import social_buzz_score


def _safe_sum(expr_fn: object, col: str) -> float:
    # expr_fn is a zero-arg callable: building the expression already fails
    # when the source table is missing, so construction goes inside the try.
    try:
        df = expr_fn().execute()
        return float(df[col].sum()) if not df.empty else 0.0
    except Exception:
        return 0.0


def build_feature_matrix(
    con: object,
    tool_repo_pairs: list[tuple[str, str]],
) -> object:
    """
    Build a feature matrix from catalog expressions for each (tool, repo) pair.
    Label = 1 if tool is in top 50% by star count (demo heuristic).
    Returns an xorq memtable expression.
    """
    rows = []
    for tool, repo in tool_repo_pairs:
        rows.append({
            "tool": tool,
            "repo": repo,
            "star_count": _safe_sum(lambda: star_velocity_30d(con, repo), "stars"),
            "pypi_downloads": _safe_sum(lambda: download_trend_90d(con, tool), "downloads"),
            "article_mentions": _safe_sum(lambda: tool_mention_frequency(con, tool), "mentions"),
            "buzz_score": _safe_sum(lambda: social_buzz_score(con, tool), "buzz_score"),
        })

    df = pd.DataFrame(rows)
    median = df["star_count"].median()
    df["label"] = (df["star_count"] >= median).astype(int)
    return xo.memtable(df)

import pandas as pd
import xorq.api as xo
from de_ecosystem.catalog.articles import tool_mention_frequency
from de_ecosystem.catalog.pypi import download_trend_90d
from de_ecosystem.catalog.github import star_velocity_30d
from de_ecosystem.catalog.social import social_buzz_score

# Signal weights — sum to 1.0
WEIGHTS = {"github": 0.40, "pypi": 0.35, "articles": 0.15, "social": 0.10}

# Normalisation ceilings (raw units that map to score=100)
CEILINGS = {"github": 500.0, "pypi": 9_000_000.0, "articles": 10.0, "social": 500.0}

# Cloud provider repo mapping
CLOUD_REPOS = {
    "azure": ["microsoft/azure-data-factory"],
    "aws": ["awslabs/aws-glue-libs"],
    "gcp": ["GoogleCloudPlatform/bigquery-utils"],
}


def _safe_sum(expr_fn: object, col: str) -> float:
    # expr_fn is a zero-arg callable: building the expression already fails
    # when the source table is missing, so construction goes inside the try.
    try:
        df = expr_fn().execute()
        return float(df[col].sum()) if not df.empty else 0.0
    except Exception:
        return 0.0


def ecosystem_health_score(
    con: object,
    tool: str,
    repo: str,
) -> object:
    """
    Composite health score 0–100 for a tool across GitHub, PyPI, RSS, and Bluesky signals.
    Returns xorq memtable with one row.
    """
    raw = {
        "github": _safe_sum(lambda: star_velocity_30d(con, repo), "stars"),
        "pypi": _safe_sum(lambda: download_trend_90d(con, tool), "downloads"),
        "articles": _safe_sum(lambda: tool_mention_frequency(con, tool), "mentions"),
        "social": _safe_sum(lambda: social_buzz_score(con, tool), "buzz_score"),
    }
    score = sum(
        min(raw[k] / CEILINGS[k], 1.0) * 100 * WEIGHTS[k]
        for k in WEIGHTS
    )
    return xo.memtable(pd.DataFrame([{
        "tool": tool,
        "repo": repo,
        "health_score": round(score, 2),
        **{f"{k}_raw": raw[k] for k in raw},
    }]))


def rising_tools(
    con: object,
    tool_repo_pairs: list[tuple[str, str]],
    top_n: int = 10,
) -> object:
    """Rank a list of (tool, repo) pairs by composite health score, return top N."""
    rows = []
    for tool, repo in tool_repo_pairs:
        row = ecosystem_health_score(con, tool, repo).execute().iloc[0].to_dict()
        rows.append(row)
    df = (
        pd.DataFrame(rows)
        .sort_values("health_score", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return xo.memtable(df)


def cloud_provider_momentum(
    con: object,
) -> object:
    """Compare Azure vs AWS vs GCP tool ecosystem activity from GitHub events."""
    t = con.table("raw_github_events")
    rows = []
    for provider, repos in CLOUD_REPOS.items():
        try:
            count = int(
                t.filter(t.repo_name.isin(repos))
                .agg(events=t.id.count())
                .execute()["events"]
                .iloc[0]
            )
        except Exception:
            count = 0
        rows.append({"provider": provider, "event_count": count})
    df = pd.DataFrame(rows).sort_values("event_count", ascending=False).reset_index(drop=True)
    return xo.memtable(df)

from datetime import datetime, timedelta
import xorq.api as xo


def star_velocity_30d(
    con: object,   # TEMPLATE: (con, repo) — bind this sentence to any repo later
    repo: str,
) -> object:
    """Stars gained per week over the last 30 days (WatchEvent = a GitHub star).

    The grammar, labeled:
      noun     -> con.table("raw_github_events")   (a lazy pointer, no compute)
      verbs    -> .filter -> .mutate -> .group_by -> .agg -> .order_by
      template -> the (con, repo) signature binds to dbt-core, polars, ...
      modifier -> which engine executes it (DuckDB / DataFusion / Snowflake)
    """
    cutoff = datetime.now() - timedelta(days=30)
    t = con.table("raw_github_events")                       # noun
    return (
        t.filter([                                           # verb
            t.repo_name == repo,
            t.type == "WatchEvent",
            t.created_at > cutoff,
        ])
        .mutate(week=t.created_at.truncate("W"))             # verb
        .group_by("week")                                    # verb
        .agg(stars=t.id.count())                             # verb
        .order_by("week")                                    # verb
    )


def pr_merge_rate(
    con: object,
    repo: str,
    days: int = 30,
) -> object:
    """Count of PR events in the last N days for a repo."""
    cutoff = datetime.now() - timedelta(days=days)
    t = con.table("raw_github_events")
    return (
        t.filter([
            t.repo_name == repo,
            t.type == "PullRequestEvent",
            t.created_at > cutoff,
        ])
        .agg(total_prs=t.id.count())
    )

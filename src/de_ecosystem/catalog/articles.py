from datetime import datetime, timedelta
import xorq.api as xo
import xorq.vendor.ibis as ibis


def tool_mention_frequency(
    con: object,
    tool: str,
    days: int = 30,
) -> object:
    """Weekly mention count of a tool keyword in article titles, last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    t = con.table("articles")
    return (
        t.filter([
            t.published_date > cutoff,
            t.title.lower().contains(tool.lower()),
        ])
        .mutate(week=t.published_date.truncate("W"))
        .group_by("week")
        .agg(mentions=t.id.count())
        .order_by("week")
    )


def source_output_rate(
    con: object,
    days: int = 30,
) -> object:
    """Average articles per week per RSS source, last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    weeks_in_window = max(days / 7.0, 1.0)
    t = con.table("articles")
    return (
        t.filter(t.published_date > cutoff)
        .group_by("source_name")
        .agg(total=t.id.count())
        .mutate(articles_per_week=(xo._.total / weeks_in_window).round(2))
        .order_by(ibis.desc("articles_per_week"))
    )

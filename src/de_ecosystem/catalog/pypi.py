from datetime import datetime, timedelta
import pandas as pd
import xorq.api as xo


def download_trend_90d(
    con: object,
    package: str,
) -> object:
    """Daily download time series for a package, last 90 days, without-mirrors only."""
    cutoff = (datetime.now() - timedelta(days=90)).date()
    t = con.table("raw_pypi_downloads")
    return (
        t.filter([
            t.package == package,
            t.category == "without_mirrors",
            t.date > cutoff,
        ])
        .select(["date", "downloads", "package"])
        .order_by("date")
    )


def adoption_acceleration(
    con: object,
    package: str,
) -> object:
    """
    Linear slope of downloads over 90 days.
    Positive = accelerating adoption; returned as xorq memtable.
    """
    trend_df = download_trend_90d(con, package).execute()
    if len(trend_df) < 4:
        return xo.memtable(pd.DataFrame([{"package": package, "slope": 0.0}]))

    n = len(trend_df)
    x = list(range(n))
    y = trend_df["downloads"].tolist()
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    slope = round(numerator / denominator, 4) if denominator else 0.0
    return xo.memtable(pd.DataFrame([{"package": package, "slope": slope}]))


def raw_download_volume(
    con: object,
    days: int = 180,
) -> object:
    """Naive leaderboard: total downloads per package (without mirrors), last N days.

    This is the 'wrong' ranking the post opens with — pydantic dominates because
    it's a transitive dependency of half of PyData, not a DE tool with momentum.
    """
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=days)).date()
    t = con.table("raw_pypi_downloads")
    return (
        t.filter([
            t.category == "without_mirrors",
            t.date > cutoff,
        ])
        .group_by("package")
        .agg(downloads=t.downloads.sum())
        .order_by(xo._.downloads.desc())  # order by the aggregated output column
    )


def download_momentum(
    con: object,
    package: str,
    window_days: int = 90,
) -> object:
    """Relative PyPI download growth: mean daily downloads over the last
    `window_days` vs the prior `window_days`, as a percent.

    Momentum is CHANGE, not volume — a huge-but-mature package (pydantic) scores
    near zero, while a smaller accelerating one scores high. Returns a 1-row memtable.
    """
    t = con.table("raw_pypi_downloads")
    df = (
        t.filter([t.package == package, t.category == "without_mirrors"])
        .select(["date", "downloads"])
        .order_by("date")
        .execute()
    )
    if df.empty:
        return xo.memtable(pd.DataFrame([{
            "package": package, "growth_pct": 0.0, "recent_daily": 0.0, "total_downloads": 0.0,
        }]))
    dates = pd.to_datetime(df["date"])
    age = (dates.max() - dates).dt.days
    recent = df.loc[age < window_days, "downloads"]
    prior = df.loc[(age >= window_days) & (age < 2 * window_days), "downloads"]
    recent_avg = float(recent.mean()) if len(recent) else 0.0
    prior_avg = float(prior.mean()) if len(prior) else 0.0
    growth = round(100.0 * (recent_avg - prior_avg) / prior_avg, 1) if prior_avg else 0.0
    return xo.memtable(pd.DataFrame([{
        "package": package,
        "growth_pct": growth,
        "recent_daily": round(recent_avg),
        "total_downloads": float(df["downloads"].sum()),
    }]))

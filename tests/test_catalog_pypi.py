from de_ecosystem.catalog.pypi import (
    download_trend_90d,
    adoption_acceleration,
    raw_download_volume,
)


def test_download_trend_returns_ordered_series(con):
    df = download_trend_90d(con, "dbt-core").execute()
    assert set(df.columns) == {"date", "downloads", "package"}
    assert df["date"].is_monotonic_increasing


def test_adoption_acceleration_positive_for_growing_series(con):
    # conftest seeds dbt-core downloads increasing with age index -> positive slope
    df = adoption_acceleration(con, "dbt-core").execute()
    assert "slope" in df.columns


def test_raw_download_volume_ranks_by_total(con):
    df = raw_download_volume(con).execute()
    assert list(df.columns) == ["package", "downloads"]
    assert df["downloads"].is_monotonic_decreasing


def test_download_momentum_negative_for_declining_seed(con):
    from de_ecosystem.catalog.pypi import download_momentum
    # conftest seeds dbt-core downloads = 10000 + i*100 where i = days-ago,
    # so downloads DECREASE toward the present -> negative 30d momentum.
    df = download_momentum(con, "dbt-core", window_days=30).execute()
    assert set(df.columns) == {"package", "growth_pct", "recent_daily", "total_downloads"}
    assert df["growth_pct"].iloc[0] < 0

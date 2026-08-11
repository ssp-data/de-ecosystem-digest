import pandas as pd


def test_digest_builders_return_frames(con):
    from digest import build_momentum, build_naive
    momentum = build_momentum(con, ["dbt-core", "polars"], window_days=30)
    naive = build_naive(con)
    assert isinstance(momentum, pd.DataFrame)
    assert {"growth_pct", "buzz"}.issubset(momentum.columns)
    assert isinstance(naive, pd.DataFrame) and "downloads" in naive.columns

from de_ecosystem.catalog.composite import ecosystem_health_score, rising_tools


def test_health_score_in_range(con):
    df = ecosystem_health_score(con, "dbt-core", "dbt-labs/dbt-core").execute()
    score = df["health_score"].iloc[0]
    assert 0.0 <= score <= 100.0


def test_rising_tools_ranks_descending(con):
    pairs = [("dbt-core", "dbt-labs/dbt-core"), ("polars", "pola-rs/polars")]
    df = rising_tools(con, pairs, top_n=5).execute()
    assert df["health_score"].is_monotonic_decreasing
    assert len(df) <= 5

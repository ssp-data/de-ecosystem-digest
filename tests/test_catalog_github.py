from de_ecosystem.catalog.github import star_velocity_30d, pr_merge_rate


def test_star_velocity_counts_watch_events(con):
    df = star_velocity_30d(con, "dbt-labs/dbt-core").execute()
    assert set(df.columns) == {"week", "stars"}
    assert df["stars"].sum() >= 1


def test_pr_merge_rate_counts_pr_events(con):
    df = pr_merge_rate(con, "dbt-labs/dbt-core").execute()
    assert int(df["total_prs"].iloc[0]) >= 1

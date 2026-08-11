from de_ecosystem.catalog.articles import tool_mention_frequency, source_output_rate


def test_tool_mention_frequency_counts_dbt(con):
    df = tool_mention_frequency(con, "dbt").execute()
    assert df["mentions"].sum() >= 1
    assert set(df.columns) == {"week", "mentions"}


def test_source_output_rate_has_per_week_column(con):
    df = source_output_rate(con).execute()
    assert "articles_per_week" in df.columns
    assert (df["articles_per_week"] > 0).all()

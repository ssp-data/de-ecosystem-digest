from de_ecosystem.catalog.social import social_buzz_score, trending_hashtags


def test_buzz_score_weights_engagement(con):
    df = social_buzz_score(con, "duckdb").execute()
    row = df.iloc[0]
    assert row["post_count"] >= 1
    # score = posts + likes*2 + reposts*3
    assert row["buzz_score"] == row["post_count"] + row["total_likes"] * 2 + row["total_reposts"] * 3


def test_trending_hashtags_returns_counts(con):
    df = trending_hashtags(con).execute()
    assert set(df.columns) == {"hashtag", "post_count"}

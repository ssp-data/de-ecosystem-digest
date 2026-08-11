import duckdb


def test_ingest_modules_import():
    from de_ecosystem.ingest import rss, bluesky, pypi, github
    assert hasattr(rss, "run_rss_pipeline")
    assert hasattr(bluesky, "run_bluesky_pipeline")
    assert hasattr(pypi, "load_pypi")
    assert hasattr(github, "load_github")


def test_github_loader_handles_missing_files(tmp_path):
    from de_ecosystem.ingest.github import load_github_dev
    con = duckdb.connect(str(tmp_path / "t.duckdb"))
    load_github_dev(con, data_glob=str(tmp_path / "nope-*.json.gz"))
    # table is created even when no files match; stays empty
    rows = con.execute("SELECT count(*) FROM raw_github_events").fetchone()[0]
    assert rows == 0


def test_bluesky_hashtag_extraction():
    from de_ecosystem.ingest.bluesky import _extract_hashtags
    facets = [{"features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "duckdb"}]}]
    assert _extract_hashtags(facets) == ["duckdb"]

def test_run_on_engine_matches_across_embedded():
    from engines import run_on_engine
    duck = run_on_engine("duckdb")
    fusion = run_on_engine("datafusion")
    # both embedded engines run the same expression on the same DuckDB source
    assert duck["ok"] is True and fusion["ok"] is True
    assert duck["total_stars"] == fusion["total_stars"]


def test_snowflake_skips_gracefully_without_creds(monkeypatch):
    from engines import run_on_engine
    # Force connect_env to fail -> must be caught and reported, not raised.
    import xorq.api as xo
    monkeypatch.setattr(xo.snowflake, "connect_env",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no creds")))
    result = run_on_engine("snowflake")
    assert result["ok"] is False and "skip" in result["note"].lower()

import pandas as pd
from de_ecosystem.settings import Settings


def test_default_engine_is_datafusion():
    assert Settings().engine == "datafusion"


def test_backend_duckdb_and_datafusion_run_same_expression():
    s = Settings()
    for engine in ("datafusion", "duckdb"):
        con = s.backend(engine)
        con.create_table("t", pd.DataFrame({"x": [1, 2, 3]}), overwrite=True)
        out = con.table("t").agg(total=con.table("t").x.sum()).execute()
        assert int(out["total"].iloc[0]) == 6


def test_load_tables_skips_missing_silently(tmp_path):
    s = Settings(db_path=str(tmp_path / "empty.duckdb"))
    con = s.backend("datafusion")
    s.load_tables_to_backend(con)  # no DuckDB file/tables yet — must not raise

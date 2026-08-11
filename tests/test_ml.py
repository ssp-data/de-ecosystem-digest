import pandas as pd
from de_ecosystem.ml.models import train_and_predict


def test_train_and_predict_returns_predictions(con):
    pairs = [
        ("dbt-core", "dbt-labs/dbt-core"),
        ("polars", "pola-rs/polars"),
        ("duckdb", "duckdb/duckdb"),
        ("dlt", "dlt-hub/dlt"),
    ]
    out = train_and_predict(con, pairs)
    assert isinstance(out, pd.DataFrame)
    assert "tool" in out.columns and "prediction" in out.columns
    assert len(out) >= 1

from __future__ import annotations
from typing import Any, Literal
from pydantic_settings import BaseSettings
import duckdb
import xorq.api as xo
from de_ecosystem.stack import stack

# Tables written by the dlt ingest layer that catalog expressions read.
RAW_TABLES = ["articles", "posts", "raw_pypi_downloads", "raw_github_events"]

Engine = Literal["duckdb", "datafusion", "snowflake"]


class Settings(BaseSettings):
    engine: Engine = stack.engine
    db_path: str = stack.db_path
    bsky_feed_uri: str = ""

    model_config = {"env_prefix": "DE_", "env_file": ".env", "extra": "ignore"}

    def backend(self, engine: Engine | None = None) -> Any:
        """Return a xorq backend for the given engine (defaults to settings.engine).

        Snowflake reads credentials from SNOWFLAKE_* env vars via connect_env().
        """
        engine = engine or self.engine
        if engine == "duckdb":
            return xo.duckdb.connect()
        if engine == "snowflake":
            # connect_env() reads SNOWFLAKE_* from os.environ, but pydantic only
            # loads DE_* — so surface the .env SNOWFLAKE_* vars into the environment.
            from dotenv import load_dotenv
            load_dotenv(self.model_config.get("env_file", ".env"))
            return xo.snowflake.connect_env()
        return xo.connect()  # datafusion (embedded default)

    def duck_connection(self) -> duckdb.DuckDBPyConnection:
        """Raw DuckDB connection — used by the ingest layer to write raw tables."""
        return duckdb.connect(self.db_path)

    def load_tables_to_backend(self, con: Any, tables: list[str] = RAW_TABLES) -> None:
        """Bridge: copy dlt-written DuckDB tables into the chosen xorq backend.

        Missing tables (nothing ingested yet) are skipped silently so the
        catalog demos degrade to "(no data)" rather than crashing.
        """
        duck = self.duck_connection()
        for table in tables:
            try:
                df = duck.execute(f"SELECT * FROM {table}").df()
                con.create_table(table, df, overwrite=True)
            except Exception:
                pass
        duck.close()

    def github_data_glob(self) -> str:
        return stack.github_slice


settings = Settings()

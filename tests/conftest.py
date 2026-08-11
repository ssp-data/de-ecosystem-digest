import pytest
import pandas as pd
import xorq.api as xo
from datetime import datetime, timedelta

NOW = datetime.now()


@pytest.fixture
def con():
    """xorq DataFusion backend seeded with all raw tables."""
    backend = xo.connect()
    _seed_articles(backend)
    _seed_pypi(backend)
    _seed_github(backend)
    _seed_posts(backend)
    return backend


def _seed_articles(backend):
    now = NOW
    df = pd.DataFrame([
        {"id": "1", "published_date": now - timedelta(days=1),
         "source_name": "dbt Blog", "author": "Alice",
         "title": "dbt-core v1.8 released with polars support",
         "url": "https://example.com/1", "word_count": 500},
        {"id": "2", "published_date": now - timedelta(days=3),
         "source_name": "Dagster Blog", "author": "Bob",
         "title": "Dagster and dlt integration guide",
         "url": "https://example.com/2", "word_count": 800},
        {"id": "3", "published_date": now - timedelta(days=7),
         "source_name": "dbt Blog", "author": "Alice",
         "title": "polars vs pandas benchmark 2024",
         "url": "https://example.com/3", "word_count": 1200},
        {"id": "4", "published_date": now - timedelta(days=10),
         "source_name": "Motherduck Blog", "author": "Carol",
         "title": "DuckDB 1.0 is here",
         "url": "https://example.com/4", "word_count": 600},
        {"id": "5", "published_date": now - timedelta(days=40),
         "source_name": "dbt Blog", "author": "Alice",
         "title": "Old dbt article outside 30-day window",
         "url": "https://example.com/5", "word_count": 400},
    ])
    backend.create_table("articles", df, overwrite=True)


def _seed_pypi(backend):
    now = NOW
    rows = []
    for i in range(90):
        date = (now - timedelta(days=i)).date()
        rows.append({"date": date, "downloads": 10000 + i * 100,
                     "category": "without_mirrors", "package": "dbt-core"})
        rows.append({"date": date, "downloads": 5000 + i * 50,
                     "category": "without_mirrors", "package": "polars"})
    backend.create_table("raw_pypi_downloads", pd.DataFrame(rows), overwrite=True)


def _seed_github(backend):
    now = NOW
    rows = []
    for i in range(30):
        dt = now - timedelta(days=i)
        rows.append({"id": f"w{i}", "created_at": dt,
                     "type": "WatchEvent", "repo_name": "dbt-labs/dbt-core",
                     "actor_login": f"user{i}"})
        if i % 3 == 0:
            rows.append({"id": f"p{i}", "created_at": dt,
                         "type": "PullRequestEvent", "repo_name": "dbt-labs/dbt-core",
                         "actor_login": f"dev{i}"})
    rows.append({"id": "wp1", "created_at": now - timedelta(days=1),
                 "type": "WatchEvent", "repo_name": "pola-rs/polars",
                 "actor_login": "user_polars"})
    backend.create_table("raw_github_events", pd.DataFrame(rows), overwrite=True)


def _seed_posts(backend):
    now = NOW
    df = pd.DataFrame([
        {"id": "p1", "created_at": now - timedelta(days=1),
         "author_handle": "alice.bsky.social", "text": "DuckDB is fast #duckdb",
         "likes": 50, "reposts": 10, "reply_count": 5,
         "hashtags": "duckdb"},
        {"id": "p2", "created_at": now - timedelta(days=2),
         "author_handle": "bob.bsky.social", "text": "dbt-core v1.8 #dbt #dataengineering",
         "likes": 30, "reposts": 8, "reply_count": 3,
         "hashtags": "dbt dataengineering"},
        {"id": "p3", "created_at": now - timedelta(days=3),
         "author_handle": "carol.bsky.social", "text": "polars is replacing pandas #polars",
         "likes": 80, "reposts": 20, "reply_count": 12,
         "hashtags": "polars"},
    ])
    backend.create_table("posts", df, overwrite=True)

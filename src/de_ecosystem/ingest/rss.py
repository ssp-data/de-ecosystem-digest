import dlt
import feedparser
from datetime import datetime
from typing import Generator
from de_ecosystem.config import DE_FEEDS
from de_ecosystem.settings import settings


def _published_date(entry) -> datetime | None:
    """RFC-822 strings vary per feed; feedparser's parsed struct_time is reliable."""
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not parsed or not 2000 <= parsed[0] <= datetime.now().year + 1:
        return None  # year-0001 dates overflow Arrow nanosecond timestamps
    return datetime(*parsed[:6])


def _parse_feed(feed_url: str) -> Generator[dict, None, None]:
    """Parse a single RSS feed URL, yielding article dicts. Silently skips on error."""
    try:
        feed = feedparser.parse(feed_url)
        source_name = getattr(feed.feed, "title", None) or feed_url
        for entry in feed.entries:
            yield {
                "id": getattr(entry, "id", None) or entry.get("link", ""),
                "published_date": _published_date(entry),
                "source_name": source_name,
                "author": getattr(entry, "author", None),
                "title": getattr(entry, "title", ""),
                "url": getattr(entry, "link", ""),
                "word_count": len(getattr(entry, "summary", "").split()),
            }
    except Exception:
        return


@dlt.resource(write_disposition="merge", primary_key="id")
def articles(feeds: list[str] | None = None) -> Generator:
    for feed_url in (feeds or DE_FEEDS):
        yield from _parse_feed(feed_url)


@dlt.source
def rss_source(feeds: list[str] | None = None):
    return articles(feeds)


def run_rss_pipeline(db_path: str = settings.db_path) -> None:
    pipeline = dlt.pipeline(
        pipeline_name="rss_articles",
        destination=dlt.destinations.duckdb(db_path),
        dataset_name="main",
        progress="enlighten",
    )
    load_info = pipeline.run(rss_source())
    print(load_info)

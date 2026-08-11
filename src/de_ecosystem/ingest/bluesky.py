import dlt
import requests
from typing import Generator
from de_ecosystem.config import BSKY_SOURCES
from de_ecosystem.settings import settings
from de_ecosystem.stack import stack

BSKY_API = "https://public.api.bsky.app/xrpc"
MAX_PAGES = stack.bsky_max_pages  # 100 posts per page — bounds ingest on busy list feeds


def _endpoint_params(uri: str) -> tuple[str, str]:
    """Map an AT URI to its XRPC endpoint and query param name."""
    if "app.bsky.graph.list" in uri:
        return "app.bsky.feed.getListFeed", "list"
    return "app.bsky.feed.getFeed", "feed"


def _extract_hashtags(facets: list[dict]) -> list[str]:
    tags = []
    for facet in facets:
        for feature in facet.get("features", []):
            if feature.get("$type") == "app.bsky.richtext.facet#tag":
                tags.append(feature["tag"])
    return tags


def _parse_post(item: dict) -> dict:
    post = item["post"]
    record = post["record"]
    return {
        "id": post["uri"],
        "created_at": record.get("createdAt"),
        "author_handle": post["author"]["handle"],
        "text": record.get("text", ""),
        "likes": post.get("likeCount", 0),
        "reposts": post.get("repostCount", 0),
        "reply_count": post.get("replyCount", 0),
        "quotes": post.get("quoteCount", 0),
        # space-joined string: a list would become a dlt child table
        "hashtags": " ".join(_extract_hashtags(record.get("facets", []))),
    }


def _fetch_source(uri: str) -> Generator[dict, None, None]:
    endpoint, param = _endpoint_params(uri)
    params: dict = {param: uri, "limit": 100}
    for _ in range(MAX_PAGES):
        try:
            resp = requests.get(f"{BSKY_API}/{endpoint}", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return
        for item in data.get("feed", []):
            yield _parse_post(item)
        cursor = data.get("cursor")
        if not cursor:
            return
        params["cursor"] = cursor


@dlt.resource(write_disposition="merge", primary_key="id")
def posts(feed_uris: list[str] | None = None) -> Generator:
    uris = feed_uris or BSKY_SOURCES + (
        [settings.bsky_feed_uri] if settings.bsky_feed_uri else []
    )
    for uri in dict.fromkeys(uris):
        yield from _fetch_source(uri)


@dlt.source
def bluesky_source(feed_uris: list[str] | None = None):
    return posts(feed_uris)


def run_bluesky_pipeline(db_path: str = settings.db_path) -> None:
    pipeline = dlt.pipeline(
        pipeline_name="bluesky_posts",
        destination=dlt.destinations.duckdb(db_path),
        dataset_name="main",
        progress="enlighten",
    )
    load_info = pipeline.run(bluesky_source())
    print(load_info)

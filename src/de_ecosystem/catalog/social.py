from datetime import datetime, timedelta
import pandas as pd
import xorq.api as xo
import xorq.vendor.ibis as ibis


def social_buzz_score(
    con: object,
    keyword: str,
    days: int = 7,
) -> object:
    """
    Engagement-weighted buzz score for a keyword in Bluesky posts, last N days.
    Score = post_count + likes*2 + reposts*3.
    Returns xorq memtable with one row.
    """
    cutoff = datetime.now() - timedelta(days=days)
    t = con.table("posts")
    filtered = t.filter([
        t.created_at > cutoff,
        t.text.lower().contains(keyword.lower()),
    ])
    agg = filtered.agg(
        post_count=t.id.count(),
        total_likes=t.likes.sum(),
        total_reposts=t.reposts.sum(),
    ).execute()

    row = agg.iloc[0]
    import math
    post_count = int(row["post_count"] or 0)
    raw_likes = row.get("total_likes")
    raw_reposts = row.get("total_reposts")
    total_likes = 0 if (raw_likes is None or (isinstance(raw_likes, float) and math.isnan(raw_likes))) else int(raw_likes)
    total_reposts = 0 if (raw_reposts is None or (isinstance(raw_reposts, float) and math.isnan(raw_reposts))) else int(raw_reposts)
    buzz = post_count + total_likes * 2 + total_reposts * 3

    return xo.memtable(pd.DataFrame([{
        "keyword": keyword,
        "post_count": post_count,
        "total_likes": total_likes,
        "total_reposts": total_reposts,
        "buzz_score": buzz,
    }]))


def trending_hashtags(
    con: object,
    days: int = 7,
    top_n: int = 10,
) -> object:
    """Top N hashtags by post count from Bluesky DE feed, last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    t = con.table("posts")
    df = t.filter(t.created_at > cutoff).execute()

    all_tags: list[str] = []
    for tags in df["hashtags"]:
        if isinstance(tags, str):
            all_tags.extend(t for t in tags.split() if t)

    if not all_tags:
        return xo.memtable(pd.DataFrame(columns=["hashtag", "post_count"]))

    from collections import Counter
    counts = Counter(all_tags).most_common(top_n)
    result_df = pd.DataFrame(counts, columns=["hashtag", "post_count"])
    return xo.memtable(result_df)

"""Filter local GH Archive hours down to DE-repo events -> one small NDJSON.gz.

Reads from a source glob (default: the reference repo's downloaded hours) and
writes data/raw/gharchive/de-slice.json.gz with only rows whose repo.name is in
DE_REPOS. Run once to (re)generate the committed slice:

    uv run python scripts/make_gh_slice.py \
        --src '/home/sspaeti/Documents/work/xorq/de-ecosystem-digest/data/raw/gharchive/*.json.gz'
"""
import argparse
import duckdb
from de_ecosystem.config import DE_REPOS

OUT = "data/raw/gharchive/de-slice.json.gz"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="glob of source GH Archive .json.gz hours")
    args = ap.parse_args()

    repo_list = ", ".join(f"'{r}'" for r in DE_REPOS)
    con = duckdb.connect()
    con.execute(f"""
        COPY (
            SELECT *
            FROM read_ndjson_auto('{args.src}', ignore_errors := true)
            WHERE repo.name IN ({repo_list})
        ) TO '{OUT}' (FORMAT JSON, COMPRESSION GZIP)
    """)
    n = con.execute(
        f"SELECT count(*) FROM read_ndjson_auto('{OUT}', ignore_errors := true)"
    ).fetchone()[0]
    print(f"wrote {OUT} with {n} events")


if __name__ == "__main__":
    main()

"""The grammar of data, one part of speech at a time.

Usage: uv run python grammar.py <noun|verb|template|modifier|run-sentence>
Driven by the pedagogical Makefile targets (make noun, make verb, ...).
"""
import sys

from de_ecosystem.settings import settings
from de_ecosystem.catalog.github import star_velocity_30d

REPO = "dbt-labs/dbt-core"


def _con():
    con = settings.backend()
    settings.load_tables_to_backend(con)
    return con


def noun() -> None:
    """A source: a lazy pointer to data, no computation yet."""
    print(">> con.table('raw_github_events')   — an unbound xorq table, no execution (NOUN)\n")
    con = _con()
    t = con.table("raw_github_events")
    print("NOUN — a source, referenced but not acted on:\n")
    print("  con.table('raw_github_events')")
    print("\nSchema (known without reading any rows):\n")
    print(t.schema())


def verb() -> None:
    """Transforms applied to the noun — the expression is built but NOT executed."""
    print(">> star_velocity_30d(con, repo)      — builds a deferred expression, not run (VERB)\n")
    con = _con()
    expr = star_velocity_30d(con, REPO)
    print("VERB — filter/mutate/group_by/agg/order_by compose a sentence.")
    print("The expression is fully built but unexecuted (deferred):\n")
    print(repr(expr))


def template() -> None:
    """The (con, repo) signature binds the same sentence to different nouns."""
    print(">> star_velocity_30d(con, <repo>)    — one expression bound to each repo (TEMPLATE)\n")
    con = _con()
    print("TEMPLATE — one sentence, bound to many repos:\n")
    for repo in (REPO, "pola-rs/polars", "duckdb/duckdb"):
        rows = len(star_velocity_30d(con, repo).execute())
        print(f"  star_velocity_30d(con, '{repo}')  ->  {rows} week-rows")


def modifier() -> None:
    """A modifier rides alongside without changing what is computed — here, the engine binding."""
    print(">> settings.backend(<engine>)        — rebind the same expression to another engine (MODIFIER)\n")
    print("MODIFIER — same expression, different engine binding:\n")
    for engine in ("datafusion", "duckdb"):
        con = settings.backend(engine)
        settings.load_tables_to_backend(con)
        total = int(star_velocity_30d(con, REPO).execute()["stars"].sum() or 0)
        print(f"  engine={engine:11}  total_stars={total}")
    print("\n(In ML, `fit` attaches another kind of modifier: 'this is a fitted model'.)")


def run_sentence() -> None:
    """Execute the full sentence end-to-end — the digest."""
    print(">> digest.main()  ->  .execute()      — say the whole sentence out loud (RUN)\n")
    print("RUN-SENTENCE — say the whole thing out loud:\n")
    import digest
    digest.main()


def lineage() -> None:
    """What xorq tracks about the sentence BEFORE it runs — sources, SQL, engine."""
    import xorq.vendor.ibis as ibis
    con = _con()
    expr = star_velocity_30d(con, REPO)
    print("LINEAGE — what xorq knows before any data is read:\n")

    print(">> expr.op().find(DatabaseTable)   — the source nouns this expression reads:")
    tables = sorted({n.name for n in expr.op().find(ibis.expr.operations.DatabaseTable)})
    print(f"     {tables}\n")

    print(">> expr.schema()                   — the output columns (resolved at build time):")
    print(f"     {expr.schema()}\n")

    print(">> expr.ls.backends                — the engine(s) bound to it (MODIFIER):")
    print(f"     {[type(b).__name__ for b in expr.ls.backends]}\n")

    print(">> ibis.to_sql(expr)               — the VERB chain, compiled to SQL:")
    print(ibis.to_sql(expr))
    print("\nThe full persisted lineage lives in builds/<hash>/expr.yaml after `make manifest`.")


DISPATCH = {
    "noun": noun,
    "verb": verb,
    "template": template,
    "modifier": modifier,
    "lineage": lineage,
    "run-sentence": run_sentence,
}


def main() -> None:
    part = sys.argv[1] if len(sys.argv) > 1 else "run-sentence"
    fn = DISPATCH.get(part)
    if fn is None:
        print(f"unknown part: {part}; choose from {', '.join(DISPATCH)}")
        sys.exit(2)
    fn()


if __name__ == "__main__":
    main()

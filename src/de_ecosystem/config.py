# Vendor / project blogs
VENDOR_FEEDS: list[str] = [
    "https://www.getdbt.com/blog/rss.xml",
    "https://dagster.io/blog/rss.xml",
    "https://airbyte.com/blog/rss.xml",
    "https://preset.io/blog/rss.xml",
    "https://motherduck.com/blog/rss.xml",
    "https://ibis-project.org/blog/rss.xml",
    "https://www.astronomer.io/blog/rss.xml",
    "https://www.datafold.com/blog/rss.xml",
    "https://towardsdatascience.com/feed",
]

# Personal DE blogs and newsletters
# (data-tagged feeds from https://www.ssp.sh/brain/rss-feeds-for-data-engineering)
COMMUNITY_FEEDS: list[str] = [
    "https://www.blef.fr/blog/rss/",
    "https://seattledataguy.substack.com/feed",
    "https://www.theseattledataguy.com/feed/",
    "https://www.confessionsofadataguy.com/feed/",
    "https://petrjanda.substack.com/feed",
    "https://stkbailey.substack.com/feed",
    "https://benn.substack.com/feed",
    "https://www.dataengineeringweekly.com/feed",
    "https://medium.com/feed/@maximebeauchemin",
    "https://davidsj.substack.com/feed",
    "https://fromanengineersight.substack.com/feed",
    "https://groupby1.substack.com/feed",
    "https://roundup.getdbt.com/feed",
    "https://pedram.substack.com/feed",
    "https://mehdio.substack.com/feed",
    "https://msmullins.substack.com/feed",
    "https://fieldnotesondata.substack.com/feed",
    "https://moderndata101.substack.com/feed",
    "https://www.kahandatasolutions.com/blog.rss",
    "https://semanticinsight.wordpress.com/feed/",
    "https://tobilg.com/rss.xml",
    "https://tayloramurphy.substack.com/feed",
    "https://win.hyperquery.ai/feed",
    "https://eczachly.substack.com/feed",
    "https://dataengineeringcentral.substack.com/feed",
    "https://moderndataengineering.substack.com/feed",
    "https://sqlpatterns.com/feed",
    "https://www.datatinkerer.io/feed",
    "https://uncledata.substack.com/feed",
    "https://joereis.substack.com/feed",
    "https://practicaldatamodeling.substack.com/feed",
    "https://dataarchitecture.substack.com/feed",
    "https://juhache.substack.com/feed",
    "https://sympathetic.ink/feed.xml",
    "https://askvinnie.substack.com/feed",
    "https://materializedview.io/feed",
    "https://www.pracdata.io/feed",
    "https://rmoff.net/index.xml",
    "https://blog.christoolivier.com/feed",
    "https://dataengineeringcommunity.substack.com/feed",
    "https://dataespresso.substack.com/feed",
    "https://datajargon.substack.com/feed",
    "https://thedatatoolbox.substack.com/feed",
    "https://groupby1.mattarderne.com/feed",
    "https://blog.mehdio.com/feed",
    "https://alirezasadeghi1.substack.com/feed",
    "https://boundlessnotions.substack.com/feed",
    "https://dataproducts.substack.com/feed",
    "https://blog.dataexpert.io/feed",
    "https://archiew.substack.com/feed",
    "https://dataopsleadership.substack.com/feed",
    "https://databased.pedramnavid.com/feed",
    "https://sarahsnewsletter.substack.com/feed",
    "https://hubertdulay.substack.com/feed",
    "https://themetagridnotes.substack.com/feed",
]

DE_FEEDS: list[str] = VENDOR_FEEDS + COMMUNITY_FEEDS

# Bluesky sources: a feed generator (getFeed) and a DE people list (getListFeed).
# https://bsky.app/profile/did:plc:edglm4muiyzty2snc55ysuqx/feed/aaaaiwku4msx6
# https://bsky.app/profile/did:plc:edglm4muiyzty2snc55ysuqx/lists/3l6zjwqkxeh2r
BSKY_SOURCES: list[str] = [
    "at://did:plc:edglm4muiyzty2snc55ysuqx/app.bsky.feed.generator/aaaaiwku4msx6",
    "at://did:plc:edglm4muiyzty2snc55ysuqx/app.bsky.graph.list/3l6zjwqkxeh2r",
]

DE_REPOS: list[str] = [
    "dbt-labs/dbt-core",
    "dagster-io/dagster",
    "dlt-hub/dlt",
    "ibis-project/ibis",
    "xorq-labs/xorq",
    "apache/airflow",
    "pola-rs/polars",
    "duckdb/duckdb",
    "great-expectations/great_expectations",
    "apache/iceberg",
    "prefecthq/prefect",
    "mage-ai/mage-ai",
    "TobikoData/sqlmesh",
    "evidence-dev/evidence",
    "rilldata/rill",
    "sodadata/soda-core",
    "sqlglot/sqlglot",
    "open-metadata/OpenMetadata",
    "microsoft/azure-data-factory",
    "awslabs/aws-glue-libs",
]

# PyPI package names (may differ from GitHub repo names)
DE_TOOLS: list[str] = [
    "dbt-core",
    "dagster",
    "dlt",
    "ibis-framework",
    "xorq",
    "apache-airflow",
    "polars",
    "duckdb",
    "great-expectations",
    "pyiceberg",
    "prefect",
    "mage-ai",
    "sqlmesh",
    "soda-core",
    "pydantic",
    "sqlglot",
]

# Correct PyPI-package -> GitHub-repo mapping. DE_TOOLS and DE_REPOS are NOT
# index-aligned, so zip() mispairs them past index 12 — use this dict instead.
TOOL_REPOS: dict[str, str] = {
    "dbt-core": "dbt-labs/dbt-core",
    "dagster": "dagster-io/dagster",
    "dlt": "dlt-hub/dlt",
    "ibis-framework": "ibis-project/ibis",
    "xorq": "xorq-labs/xorq",
    "apache-airflow": "apache/airflow",
    "polars": "pola-rs/polars",
    "duckdb": "duckdb/duckdb",
    "great-expectations": "great-expectations/great_expectations",
    "pyiceberg": "apache/iceberg",
    "prefect": "prefecthq/prefect",
    "mage-ai": "mage-ai/mage-ai",
    "sqlmesh": "TobikoData/sqlmesh",
    "soda-core": "sodadata/soda-core",
    "sqlglot": "tobymao/sqlglot",
    "pydantic": "pydantic/pydantic",
}

# Substring keyword to match a tool in free-text Bluesky posts. Tools not listed
# here use their own name as the keyword.
TOOL_KEYWORDS: dict[str, str] = {
    "dbt-core": "dbt",
    "apache-airflow": "airflow",
    "pyiceberg": "iceberg",
    "ibis-framework": "ibis",
    "great-expectations": "great expectations",
    "soda-core": "soda",
    "mage-ai": "mage",
}

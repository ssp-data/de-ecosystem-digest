from de_ecosystem import config


def test_config_lists_are_populated():
    assert len(config.DE_FEEDS) > 30
    assert len(config.DE_TOOLS) >= 15
    assert len(config.DE_REPOS) >= 15
    assert "pydantic" in config.DE_TOOLS          # the "raw downloads lie" example
    assert "xorq-labs/xorq" in config.DE_REPOS
    assert config.BSKY_SOURCES and all(s.startswith("at://") for s in config.BSKY_SOURCES)


def test_tool_repos_mapping_is_correct():
    from de_ecosystem import config
    assert config.TOOL_REPOS["pydantic"] == "pydantic/pydantic"
    assert config.TOOL_REPOS["soda-core"] == "sodadata/soda-core"
    assert config.TOOL_REPOS["sqlglot"] == "tobymao/sqlglot"
    assert all("/" in repo for repo in config.TOOL_REPOS.values())
    assert set(config.TOOL_REPOS) == set(config.DE_TOOLS)

from de_ecosystem.stack import load_stack
from de_ecosystem.config import DE_TOOLS


def test_defaults_when_no_file(tmp_path):
    s = load_stack(str(tmp_path / "nope.yaml"))
    assert s.engine == "datafusion"
    assert s.window_days == 90
    assert s.tools == list(DE_TOOLS)


def test_yaml_overrides_defaults(tmp_path):
    f = tmp_path / "stack.yaml"
    f.write_text("engine: duckdb\nmomentum:\n  window_days: 30\n  tools: [duckdb, polars]\n")
    s = load_stack(str(f))
    assert s.engine == "duckdb"
    assert s.window_days == 30
    assert s.tools == ["duckdb", "polars"]


def test_env_overrides_yaml(tmp_path, monkeypatch):
    f = tmp_path / "stack.yaml"
    f.write_text("momentum:\n  window_days: 30\n")
    monkeypatch.setenv("DE_WINDOW_DAYS", "60")
    s = load_stack(str(f))
    assert s.window_days == 60

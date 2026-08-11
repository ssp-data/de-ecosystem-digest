import subprocess
import sys


def test_expr_runs_without_error():
    # Runs against whatever de_ecosystem.duckdb exists (may be empty) — must not crash.
    result = subprocess.run(
        [sys.executable, "expr.py"],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stderr
    assert "Backend:" in result.stdout

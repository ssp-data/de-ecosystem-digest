import subprocess
import sys
import pytest


@pytest.mark.parametrize("part", ["noun", "verb", "template", "modifier", "lineage", "run-sentence"])
def test_grammar_parts_run(part):
    result = subprocess.run(
        [sys.executable, "grammar.py", part],
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stderr

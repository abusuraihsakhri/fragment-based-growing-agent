"""Check that the standalone browser artifact includes valid JavaScript."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HTML = Path(__file__).resolve().parents[1] / "web" / "index.html"


def test_static_web_entry_and_js_syntax():
    source = HTML.read_text(encoding="utf-8")
    assert "<form id=\"ro3-form\">" in source
    assert "<form id=\"audit-form\">" in source
    assert "fetch('/api/audit'" not in source
    scripts = re.findall(r"<script>(.*?)</script>", source, re.DOTALL)
    assert len(scripts) == 1
    if not shutil.which("node"):
        pytest.skip("Node.js not available for JavaScript syntax check")
    result = subprocess.run(["node", "--check", "-"], input=scripts[0],
                            text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr

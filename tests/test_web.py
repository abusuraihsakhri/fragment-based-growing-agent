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


def test_browser_logic_smoke():
    if not shutil.which("node"):
        pytest.skip("Node.js not available for browser script smoke test")
    source = HTML.read_text(encoding="utf-8")
    js = re.findall(r"<script>(.*?)</script>", source, re.DOTALL)[0]
    harness = r"""
const vm = require('vm');
const fs = require('fs');
const script = fs.readFileSync(0, 'utf8');
const nodes = {};
const listeners = {};
const defaults = {mw:'245',clogp:'2.1',hbd:'2',hba:'3',
  primary:'28.5',secondary:'14.2',task:'T-1',descriptor:'NOMINAL'};
const document = {
  getElementById(id) {
    if (!nodes[id]) {
      nodes[id] = {value: defaults[id] || '', checked: false, disabled: true,
        dataset: {}, textContent: '', previousElementSibling: {textContent: id},
        addEventListener(name, fn) {listeners[id + ':' + name] = fn;}};
    }
    return nodes[id];
  }
};
vm.runInNewContext(script, {document, console, Blob, URL, setTimeout});
function submit(id) {listeners[id + ':submit']({preventDefault(){}});}
function result(id) {return JSON.parse(nodes[id].textContent);}
submit('ro3-form');
if (!result('ro3-result').passes) throw Error('Expected Ro3 pass');
nodes.mw.value = '300';
submit('ro3-form');
if (result('ro3-result').passes) throw Error('Expected Ro3 fail at MW=300');
submit('audit-form');
if (result('audit-result').overall_urgency !== 'ELEVATED_RISK') throw Error('Expected warning');
nodes.critical.checked = true;
submit('audit-form');
if (result('audit-result').overall_urgency !== 'CRITICAL_STAT_PANIC') throw Error('Expected critical');
if (nodes['download-ro3'].disabled || nodes['download-audit'].disabled) throw Error('Export disabled');
"""
    run = subprocess.run(["node", "-e", harness], input=js, text=True,
                         capture_output=True, check=False)
    assert run.returncode == 0, run.stderr

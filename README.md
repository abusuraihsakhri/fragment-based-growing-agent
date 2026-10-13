# Fragment Based Growing Agent

Python prototypes for descriptor-based fragment screening and configurable, rule-based telemetry checks. The project includes a standalone browser interface, two legacy Python audit implementations, a FastAPI service, and regression tests.

## What works

- **Rule-of-Three screening:** evaluate provided molecular weight, calculated logP, hydrogen-bond donor count, and acceptor count against MW < 300 Da, cLogP ≤ 3, HBD ≤ 3 and HBA ≤ 3.
- **Browser application:** open `web/index.html` directly to evaluate descriptors or inspect the legacy heuristic locally, then export results as JSON. It does not require an API.
- **Python command line:** inspect one task, process batches of CSV records, view mock supervisor responses, or serve the API.
- **FastAPI service:** `/health`, `/api/audit`, `/api/chat`, Prometheus text at `/metrics`, summary JSON at `/api/metrics`, and in-memory audit verification at `/api/audit/logs`.
- **Tamper-evident audit chain:** HMAC-SHA256 signature verification for the `agents/` workflow, with optional operator-provided secret.

**Scope limitations:** The existing `agents/` and `fragment_grow/` telemetry checks use generic numeric thresholds and descriptor keywords. They are *not* conformant fragment-growing, docking, SAR, SAscore, or pharmacophore-vector algorithms. The Rule-of-Three assessment works on supplied descriptors; it does not parse SMILES or compute molecular properties. Screening thresholds are heuristics, not evidence of binding, biological activity, safety, or synthesizability.

## Browser use

Open `web/index.html` in a modern browser. Enter the four fragment descriptors, run the Rule-of-Three screen and export JSON if needed. A separate legacy threshold form implements the `agents/` defaults (primary > 25, secondary > 12, critical flag, and descriptor keywords). No server request is made by the static page. GitHub Pages deployment is configured in `.github/workflows/ci.yml` for pushes to `master`, but requires Pages to be enabled with GitHub Actions as the publication source.

## Python installation and CLI

Requires Python 3.9 or later.

```bash
python -m pip install -e ".[server,test]"
python cli.py ro3 --mw 245 --clogp 2.1 --hbd 2 --hba 3
python cli.py audit --task-id TEST-01 --target TARGET-01 --primary 28.5 --secondary 14.2
python cli.py batch --input sample.csv --output results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The packaged `fragment-based-growing-agent` command invokes the `agents/` implementation via root `cli.py`. The historical `fragment-based-growing-engine` command invokes `fragment_grow/cli.py`; its output schemas and secondary threshold differ. Both command-line interfaces support `ro3`, `audit`, `batch`, `chat` and `serve`; only the first exposes `verify-audit`. Use `--help` for command options.

### API example

```bash
curl -X POST http://127.0.0.1:8000/api/audit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"T-1","target_identifier":"fragment-A","primary_metric":12,"secondary_metric":4,"status_descriptor":"NOMINAL","is_critical_flag":false}'
```

## Security and privacy

The browser interface runs locally, without network requests or uploads. The Python API is intended for controlled local use; it **has no authentication or rate limiting** and should not be exposed directly to the public internet. The regex-based sensitive-identifier guard is incomplete and does not establish HIPAA compliance or guaranteed PHI removal. Do not supply patient information or confidential data.

The audit trail is maintained **in memory** and is lost at process shutdown. Set `AUDIT_SECRET_KEY` to a unique secret managed outside source control when stable signature keys are needed; otherwise a random process-local key is generated. Rotating any previously hard-coded keys is recommended. The endpoint `/api/audit/logs` is disabled unless `AUDIT_LOGS_TOKEN` is set; once configured it requires the HTTP header `Authorization: Bearer <token>`. Protect the service behind authentication at the network boundary as well.

For Docker Compose, configure the secret in your environment, then run:

```bash
docker compose up --build
```

## Development and tests

```bash
python -m pip install -e ".[server,test]"
python -m pytest -q
python -m compileall -q agents fragment_grow cli.py enrichment.py simulator.py
```

Continuous integration checks Python 3.10, 3.11, and 3.12. Browser JavaScript syntax is checked with Node.js when available. The local web interface requires a modern browser with JavaScript enabled; it has no third-party runtime dependencies.

## Reference

Congreve M, Carr R, Murray C, Jhoti H. A 'Rule of Three' for fragment-based lead discovery. *Drug Discovery Today*. 2003;8:876–877. The numeric filter is one screening convention, not an absolute exclusion criterion.

## License

MIT — see [LICENSE](LICENSE).

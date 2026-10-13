"""Regression tests for security, file input and scientific-screen boundaries."""
import csv
import json
import math

import pytest
from pydantic import ValidationError

from agents.base import AuditTrail
from agents.llm_factory import LLMFactory
from agents.models import SystemTaskPayload
from agents.api import app
from cli import main as enterprise_main
from fragment_grow.cli import main as legacy_main
from fragment_grow.validation import parse_csv_bool
from fragment_grow.ro3 import assess_rule_of_three


def test_audit_signature_detects_tampering_and_external_changes():
    log = AuditTrail(secret_key="test-secret")
    log.log("tester", "operator", "TEST", {"sample": "A"})
    log.log("tester", "operator", "TEST", {"sample": "B"})
    assert log.verify_integrity()
    log.get_trail()[0]["payload_hash"] = "tampered"
    assert log.verify_integrity()  # callers receive a copy
    log.logs[0]["payload_hash"] = "tampered"
    assert not log.verify_integrity()


def test_csv_boolean_parser():
    assert parse_csv_bool("False") is False
    assert parse_csv_bool("0") is False
    assert parse_csv_bool("NO") is False
    assert parse_csv_bool("TRUE") is True
    with pytest.raises(ValueError):
        parse_csv_bool("maybe")


def test_batch_false_flag_does_not_escalate(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "A,fragment,12,4,False,NOMINAL\n", encoding="utf-8"
    )
    for idx, runner in enumerate((enterprise_main, legacy_main)):
        output = tmp_path / f"out{idx}.csv"
        assert runner(["batch", "--input", str(source), "--output", str(output)]) == 0
        with output.open(newline="", encoding="utf-8") as stream:
            row = next(csv.DictReader(stream))
        if idx == 0:
            assert row["overall_urgency"] == "ROUTINE"
        else:
            assert row["overall_status"] == "NOMINAL_OPTIMAL"


def test_nonfinite_api_metrics_rejected():
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="A", target_identifier="B", primary_metric=value)


def test_unimplemented_providers_fail_explicitly():
    with pytest.raises(ValueError, match="not implemented"):
        LLMFactory.create("openai")


def test_real_rule_of_three_boundaries():
    assert assess_rule_of_three(299.9, 3, 3, 3)["passes"]
    assert not assess_rule_of_three(300, 3, 3, 3)["passes"]
    assert set(assess_rule_of_three(200, 4, 4, 1)["violations"]) == {
        "clogp", "hydrogen_bond_donors"
    }
    with pytest.raises(ValueError):
        assess_rule_of_three(math.nan, 1, 0, 0)
    with pytest.raises(ValueError):
        assess_rule_of_three(200, 1, True, 0)


def test_http_sensitive_input_and_prometheus_metrics():
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        response = client.post("/api/audit", json={
            "task_id": "T", "target_identifier": "KEY-001",
            "primary_metric": 12, "secondary_metric": 4,
            "attributes": {"email": "alice@example.com"},
        })
        assert response.status_code == 422
        assert "alice@example.com" not in response.text

        metrics = client.get("/metrics")
        assert metrics.status_code == 200
        assert "system_tasks_total" in metrics.text
        assert metrics.headers["content-type"].startswith("text/plain")
        assert client.get("/api/metrics").status_code == 200

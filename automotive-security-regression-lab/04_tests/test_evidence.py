import json

import pytest

from security_lab.evidence import (
    Evidence,
    EvidenceGenerator,
    EvidenceResult,
    EvidenceValidationError,
)
from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import ECUSimulator, ResponseStatus
from security_lab.test_runner import SecurityTestCase, SecurityTestRunner


def create_evidence(
    *,
    test_id: str = "TC-EVIDENCE-001",
    timestamp: str = "2026-08-23T12:00:00Z",
    target: str = "simulated-ecu",
    preconditions: dict | None = None,
    input_data: str = "PROTECTED_OPERATION",
    expected: str = "ACCESS_DENIED",
    actual: str = "ACCESS_DENIED",
    result: EvidenceResult = EvidenceResult.PASS,
    notes: str = "Evidence test.",
) -> Evidence:
    """Create deterministic test evidence for unit tests."""

    return Evidence(
        test_id=test_id,
        timestamp=timestamp,
        target=target,
        preconditions=preconditions or {"authorization": False},
        input=input_data,
        expected=expected,
        actual=actual,
        result=result,
        notes=notes,
    )


def test_valid_evidence_is_accepted():
    evidence = create_evidence()

    evidence.validate()


def test_missing_required_field_is_rejected():
    data = {
        "timestamp": "2026-08-23T12:00:00Z",
        "target": "simulated-ecu",
        "preconditions": {"authorization": False},
        "input": "PROTECTED_OPERATION",
        "expected": "ACCESS_DENIED",
        "actual": "ACCESS_DENIED",
        "result": "PASS",
        "notes": "Test evidence.",
    }

    with pytest.raises(EvidenceValidationError):
        Evidence.from_dict(data)


def test_missing_input_is_rejected():
    evidence = create_evidence(input_data=None)

    with pytest.raises(EvidenceValidationError):
        evidence.validate()


def test_missing_notes_is_rejected():
    evidence = create_evidence(notes="")

    with pytest.raises(EvidenceValidationError):
        evidence.validate()


def test_invalid_timestamp_is_rejected():
    evidence = create_evidence(timestamp="not-a-timestamp")

    with pytest.raises(EvidenceValidationError):
        evidence.validate()


def test_timestamp_without_timezone_is_rejected():
    evidence = create_evidence(timestamp="2026-08-23T12:00:00")

    with pytest.raises(EvidenceValidationError):
        evidence.validate()


def test_invalid_result_is_rejected():
    data = {
        "test_id": "TC-EVIDENCE-INVALID-RESULT",
        "timestamp": "2026-08-23T12:00:00Z",
        "target": "simulated-ecu",
        "preconditions": {"authorization": False},
        "input": "PROTECTED_OPERATION",
        "expected": "ACCESS_DENIED",
        "actual": "ACCESS_DENIED",
        "result": "UNKNOWN",
        "notes": "Invalid result test.",
    }

    with pytest.raises(EvidenceValidationError):
        Evidence.from_dict(data)


def test_pass_evidence_when_expected_equals_actual():
    evidence = create_evidence(
        expected="ACCESS_DENIED",
        actual="ACCESS_DENIED",
        result=EvidenceResult.PASS,
    )

    evidence.validate()

    assert evidence.result is EvidenceResult.PASS


def test_fail_evidence_when_expected_differs_from_actual():
    evidence = create_evidence(
        expected="ACCESS_DENIED",
        actual="ACCESS_GRANTED",
        result=EvidenceResult.FAIL,
        notes="Observed behavior differed from expected behavior.",
    )

    evidence.validate()

    assert evidence.result is EvidenceResult.FAIL


def test_inconsistent_pass_result_is_rejected():
    evidence = create_evidence(
        expected="ACCESS_DENIED",
        actual="ACCESS_GRANTED",
        result=EvidenceResult.PASS,
    )

    with pytest.raises(EvidenceValidationError):
        evidence.validate()


def test_inconsistent_fail_result_is_rejected():
    evidence = create_evidence(
        expected="ACCESS_DENIED",
        actual="ACCESS_DENIED",
        result=EvidenceResult.FAIL,
    )

    with pytest.raises(EvidenceValidationError):
        evidence.validate()


def test_evidence_can_be_serialized_to_json():
    evidence = create_evidence(
        test_id="TC-EVIDENCE-005",
    )

    serialized = evidence.to_json()
    data = json.loads(serialized)

    assert data["test_id"] == "TC-EVIDENCE-005"
    assert data["result"] == "PASS"
    assert data["target"] == "simulated-ecu"
    assert data["expected"] == "ACCESS_DENIED"
    assert data["actual"] == "ACCESS_DENIED"


def test_evidence_can_be_restored_from_dictionary():
    evidence = create_evidence(
        test_id="TC-EVIDENCE-RESTORE",
    )

    restored = Evidence.from_dict(evidence.to_dict())

    assert restored == evidence


def test_evidence_generator_uses_phase3_test_result():
    target = ECUAdapter(ECUSimulator())
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-EVIDENCE-006",
        description="Unauthorized protected operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_DENIED,
    )

    result = runner.run(case)

    evidence = EvidenceGenerator().generate(
        case,
        result,
        preconditions={"authorization": False},
        notes="Unauthorized protected operation was rejected.",
    )

    assert evidence.test_id == "TC-EVIDENCE-006"
    assert evidence.target == "simulated-ecu"
    assert evidence.expected == "ACCESS_DENIED"
    assert evidence.actual == "ACCESS_DENIED"
    assert evidence.result is EvidenceResult.PASS

    evidence.validate()
from security_lab.evidence import (
    Evidence,
    EvidenceGenerator,
    EvidenceResult,
    EvidenceValidationError,
)
from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import ECUSimulator, ResponseStatus
from security_lab.test_runner import SecurityTestCase, SecurityTestRunner


def test_valid_evidence_is_accepted():
    evidence = Evidence(
        test_id="TC-EVIDENCE-001",
        timestamp="2026-08-23T12:00:00Z",
        target="simulated-ecu",
        preconditions={"authorization": False},
        input="PROTECTED_OPERATION",
        expected="ACCESS_DENIED",
        actual="ACCESS_DENIED",
        result=EvidenceResult.PASS,
        notes="Unauthorized protected operation was rejected.",
    )

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

    try:
        Evidence.from_dict(data)
    except EvidenceValidationError:
        return

    raise AssertionError("Missing test_id must be rejected")


def test_pass_evidence_when_expected_equals_actual():
    evidence = Evidence(
        test_id="TC-EVIDENCE-003",
        timestamp="2026-08-23T12:00:00Z",
        target="simulated-ecu",
        preconditions={"authorization": False},
        input="PROTECTED_OPERATION",
        expected="ACCESS_DENIED",
        actual="ACCESS_DENIED",
        result=EvidenceResult.PASS,
        notes="Expected behavior observed.",
    )

    evidence.validate()

    assert evidence.result is EvidenceResult.PASS


def test_fail_evidence_when_expected_differs_from_actual():
    evidence = Evidence(
        test_id="TC-EVIDENCE-004",
        timestamp="2026-08-23T12:00:00Z",
        target="simulated-ecu",
        preconditions={"authorization": False},
        input="PROTECTED_OPERATION",
        expected="ACCESS_DENIED",
        actual="ACCESS_GRANTED",
        result=EvidenceResult.FAIL,
        notes="Observed behavior differed from expected behavior.",
    )

    evidence.validate()

    assert evidence.result is EvidenceResult.FAIL


def test_evidence_can_be_serialized_to_json():
    evidence = Evidence(
        test_id="TC-EVIDENCE-005",
        timestamp="2026-08-23T12:00:00Z",
        target="simulated-ecu",
        preconditions={"authorization": False},
        input="PROTECTED_OPERATION",
        expected="ACCESS_DENIED",
        actual="ACCESS_DENIED",
        result=EvidenceResult.PASS,
        notes="Evidence serialization test.",
    )

    serialized = evidence.to_json()

    assert '"test_id": "TC-EVIDENCE-005"' in serialized
    assert '"result": "PASS"' in serialized


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
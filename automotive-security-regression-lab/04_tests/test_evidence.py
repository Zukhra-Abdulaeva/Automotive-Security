from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import ECUSimulator, ResponseStatus
from security_lab.evidence import EvidenceGenerator
from security_lab.test_runner import SecurityTestCase, SecurityTestRunner


def test_evidence_contains_execution_result():
    target = ECUAdapter(ECUSimulator())
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-EVIDENCE-001",
        description="Unauthorized protected operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_DENIED,
    )

    result = runner.run(case)
    evidence = EvidenceGenerator().generate(case, result)

    assert evidence.test_id == "TC-EVIDENCE-001"
    assert evidence.expected_status is ResponseStatus.ACCESS_DENIED
    assert evidence.actual_status is ResponseStatus.ACCESS_DENIED
    assert evidence.passed is True
    assert evidence.operation == "PROTECTED_OPERATION"


def test_evidence_has_deterministic_execution_id_format():
    generator = EvidenceGenerator()

    target = ECUAdapter(ECUSimulator())
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-EVIDENCE-002",
        description="Authorized protected operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_GRANTED,
    )

    result = runner.run(case)
    evidence = generator.generate(case, result)

    assert evidence.execution_id == "EXEC-000001"


def test_evidence_to_dict_uses_status_values():
    target = ECUAdapter(ECUSimulator())
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-EVIDENCE-003",
        description="Invalid operation",
        request={"operation": "UNKNOWN_OPERATION"},
        expected_status=ResponseStatus.INVALID_REQUEST,
    )

    result = runner.run(case)
    evidence = EvidenceGenerator().generate(case, result)

    data = evidence.to_dict()

    assert data["expected_status"] == "INVALID_REQUEST"
    assert data["actual_status"] == "INVALID_REQUEST"
    assert data["passed"] is True
    assert data["operation"] == "UNKNOWN_OPERATION"

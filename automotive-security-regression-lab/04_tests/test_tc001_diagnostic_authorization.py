from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import ECUSimulator, ResponseStatus
from security_lab.evidence import EvidenceGenerator, EvidenceResult
from security_lab.test_runner import SecurityTestCase, SecurityTestRunner


def test_tc001_unauthorized_access_secure_ecu():
    ecu = ECUSimulator(mode="secure")
    ecu.set_authorized(False)

    target = ECUAdapter(ecu)
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-001",
        description="Unauthorized protected diagnostic operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_DENIED,
    )

    result = runner.run(case)

    assert result.passed
    assert result.expected_status is ResponseStatus.ACCESS_DENIED
    assert result.actual_status is ResponseStatus.ACCESS_DENIED


def test_tc001_authorized_access_secure_ecu():
    ecu = ECUSimulator(mode="secure")
    ecu.set_authorized(True)

    target = ECUAdapter(ecu)
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-001",
        description="Authorized protected diagnostic operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_GRANTED,
    )

    result = runner.run(case)

    assert result.passed
    assert result.expected_status is ResponseStatus.ACCESS_GRANTED
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED


def test_tc001_vulnerable_behavior_produces_security_observation():
    ecu = ECUSimulator(mode="vulnerable")
    ecu.set_authorized(False)

    target = ECUAdapter(ecu)
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-001",
        description="Unauthorized protected diagnostic operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_DENIED,
    )

    result = runner.run(case)

    assert result.expected_status is ResponseStatus.ACCESS_DENIED
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED
    assert not result.passed

    evidence = EvidenceGenerator().generate(
        case,
        result,
        target="simulated-ecu",
        preconditions={"authorization": False},
        notes="Protected operation was accepted without authorization.",
    )

    assert evidence.result is EvidenceResult.FAIL
    assert evidence.expected == "ACCESS_DENIED"
    assert evidence.actual == "ACCESS_GRANTED"


def test_tc001_vulnerable_evidence_is_machine_readable():
    ecu = ECUSimulator(mode="vulnerable")
    ecu.set_authorized(False)

    target = ECUAdapter(ecu)
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-001",
        description="Unauthorized protected diagnostic operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_DENIED,
    )

    result = runner.run(case)

    evidence = EvidenceGenerator().generate(
        case,
        result,
        target="simulated-ecu",
        preconditions={"authorization": False},
        notes="Protected operation was accepted without authorization.",
    )

    evidence_dict = evidence.to_dict()

    assert evidence_dict["test_id"] == "TC-001"
    assert evidence_dict["target"] == "simulated-ecu"
    assert evidence_dict["preconditions"]["authorization"] is False
    assert evidence_dict["expected"] == "ACCESS_DENIED"
    assert evidence_dict["actual"] == "ACCESS_GRANTED"
    assert evidence_dict["result"] == "FAIL"

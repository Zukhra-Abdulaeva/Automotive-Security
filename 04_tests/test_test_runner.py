from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import ECUSimulator, ResponseStatus
from security_lab.test_runner import SecurityTestCase, SecurityTestRunner


def test_arch_001_unauthorized_protected_operation():
    target = ECUAdapter(ECUSimulator())
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-ARCH-001",
        description="Unauthorized protected operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_DENIED,
    )

    result = runner.run(case)

    assert result.passed
    assert result.actual_status is ResponseStatus.ACCESS_DENIED


def test_arch_002_authorized_protected_operation():
    ecu = ECUSimulator()
    ecu.set_authorized(True)

    target = ECUAdapter(ecu)
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-ARCH-002",
        description="Authorized protected operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_GRANTED,
    )

    result = runner.run(case)

    assert result.passed
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED


def test_arch_003_invalid_operation():
    target = ECUAdapter(ECUSimulator())
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-ARCH-003",
        description="Invalid operation",
        request={"operation": "UNKNOWN_OPERATION"},
        expected_status=ResponseStatus.UNSUPPORTED_OPERATION,
    )

    result = runner.run(case)

    assert result.passed
    assert result.actual_status is ResponseStatus.UNSUPPORTED_OPERATION

def test_arch_004_vulnerable_unauthorized_protected_operation():
    target = ECUAdapter(ECUSimulator(mode="vulnerable"))
    runner = SecurityTestRunner(target)

    case = SecurityTestCase(
        test_id="TC-ARCH-004",
        description="Vulnerable unauthorized protected operation",
        request={"operation": "PROTECTED_OPERATION"},
        expected_status=ResponseStatus.ACCESS_GRANTED,
    )

    result = runner.run(case)

    assert result.passed
    assert result.actual_status is ResponseStatus.ACCESS_GRANTED

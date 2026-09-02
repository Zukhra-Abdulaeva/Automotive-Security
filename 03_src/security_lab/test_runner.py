"""Security test execution layer for the Automotive Security Regression Lab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from security_lab.ecu_adapter import ECUTarget
from security_lab.ecu_simulator import ResponseStatus


@dataclass(frozen=True)
class SecurityTestCase:
    """Minimal description of one security test case."""

    test_id: str
    description: str
    request: Mapping[str, Any]
    expected_status: ResponseStatus


@dataclass(frozen=True)
class TestResult:
    """Structured result of one security test execution."""

    test_id: str
    expected_status: ResponseStatus
    actual_status: ResponseStatus
    passed: bool


class SecurityTestRunner:
    """Execute security test cases against an abstract ECU target."""

    def __init__(self, target: ECUTarget) -> None:
        self._target = target

    def run(self, test_case: SecurityTestCase) -> TestResult:
        """Execute one test case and compare the actual response status."""
        response = self._target.handle_request(test_case.request)
        passed = response.status is test_case.expected_status

        return TestResult(
            test_id=test_case.test_id,
            expected_status=test_case.expected_status,
            actual_status=response.status,
            passed=passed,
        )
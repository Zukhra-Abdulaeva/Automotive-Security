"""Target adapter for the simulated ECU."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from security_lab.ecu_simulator import ECUResponse, ECUSimulator


class ECUTarget(Protocol):
    """Interface used by the security test runner to access an ECU target."""

    def handle_request(self, request: Mapping[str, Any]) -> ECUResponse:
        """Send one request to the ECU target and return its response."""
        ...


class ECUAdapter:
    """Adapter exposing the ECU simulator through the target interface."""

    def __init__(self, target: ECUSimulator) -> None:
        self._target = target

    def handle_request(self, request: Mapping[str, Any]) -> ECUResponse:
        """Forward one request to the configured ECU target."""
        return self._target.handle_request(request)
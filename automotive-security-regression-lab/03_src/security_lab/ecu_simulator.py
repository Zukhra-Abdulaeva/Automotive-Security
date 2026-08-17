"""Deterministic simulated ECU for the Automotive Security Regression Lab.


This module intentionally models only the security properties required by the project. 
It does not implement a real CAN or UDS stack, nor does it perform any network communication.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class SecurityMode(str, Enum):
    """Security policy mode of the simulated ECU."""

    SECURE = "secure"
    VULNERABLE = "vulnerable"


class Operation(str, Enum):
    """Operations understood by the simulated ECU."""

    PROTECTED_OPERATION = "PROTECTED_OPERATION"


class ResponseStatus(str, Enum):
    """Deterministic response statuses exposed by the ECU."""

    ACCESS_GRANTED = "ACCESS_GRANTED"
    ACCESS_DENIED = "ACCESS_DENIED"
    INVALID_REQUEST = "INVALID_REQUEST"


@dataclass(frozen=True)
class ECUResponse:
    """Structured response returned for every handled request."""

    status: ResponseStatus
    operation: str | None

    def to_dict(self) -> dict[str, str | None]:
        """Return a simple mapping suitable for later test/evidence layers."""
        return {
            "status": self.status.value,
            "operation": self.operation,
        }


class ECUSimulator:
    """Small deterministic ECU security target used by Phase 2 tests."""

    def __init__(self, mode: SecurityMode | str = SecurityMode.SECURE) -> None:
        try:
            self._mode = SecurityMode(mode)
        except (TypeError, ValueError) as exc:
            raise ValueError("mode must be 'secure' or 'vulnerable'") from exc

        self._authorized = False

    @property
    def mode(self) -> SecurityMode:
        """Return the configured security mode."""
        return self._mode

    @property
    def authorized(self) -> bool:
        """Return the current authorization state."""
        return self._authorized

    def set_authorized(self, authorized: bool) -> None:
        """Set authorization state explicitly."""
        if not isinstance(authorized, bool):
            raise ValueError("authorized must be a boolean")
        self._authorized = authorized

    def handle_request(self, request: Any) -> ECUResponse:
        """Validate and process one diagnostic-style request.

        Accepted request shape:
            {"operation": "PROTECTED_OPERATION"}

        An optional ``parameters`` mapping is accepted for future-proofing,
        but no parameters are currently required or interpreted.
        """
        if not isinstance(request, Mapping):
            return ECUResponse(ResponseStatus.INVALID_REQUEST, None)

        operation = request.get("operation")
        if not isinstance(operation, str) or not operation:
            return ECUResponse(ResponseStatus.INVALID_REQUEST, None)

        if operation != Operation.PROTECTED_OPERATION.value:
            return ECUResponse(ResponseStatus.INVALID_REQUEST, operation)

        if "parameters" in request and not isinstance(request["parameters"], Mapping):
            return ECUResponse(ResponseStatus.INVALID_REQUEST, operation)

        if self._mode is SecurityMode.VULNERABLE:
            return ECUResponse(ResponseStatus.ACCESS_GRANTED, operation)

        if self._authorized:
            return ECUResponse(ResponseStatus.ACCESS_GRANTED, operation)

        return ECUResponse(ResponseStatus.ACCESS_DENIED, operation)

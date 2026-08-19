from security_lab.ecu_simulator import ECUSimulator


def test_secure_unauthorized_request():
    ecu = ECUSimulator()

    response = ecu.handle_request(
        {"operation": "PROTECTED_OPERATION"}
    )

    assert response.status.value == "ACCESS_DENIED"


def test_secure_authorized_request():
    ecu = ECUSimulator()
    ecu.set_authorized(True)

    response = ecu.handle_request(
        {"operation": "PROTECTED_OPERATION"}
    )

    assert response.status.value == "ACCESS_GRANTED"

def test_vulnerable_unauthorized_request():
    ecu = ECUSimulator(mode="vulnerable")

    response = ecu.handle_request(
        {"operation": "PROTECTED_OPERATION"}
    )

    assert response.status.value == "ACCESS_GRANTED"

def test_unknown_operation():
    ecu = ECUSimulator()

    response = ecu.handle_request(
        {"operation": "UNKNOWN_OPERATION"}
    )

    assert response.status.value == "INVALID_REQUEST"

def test_invalid_input():
    ecu = ECUSimulator()

    response = ecu.handle_request(
        "INVALID_INPUT"
    )

    assert response.status.value == "INVALID_REQUEST"

def test_invalid_parameters():
    ecu = ECUSimulator()

    response = ecu.handle_request(
        {
            "operation": "PROTECTED_OPERATION",
            "parameters": "INVALID"
        }
    )

    assert response.status.value == "INVALID_REQUEST"
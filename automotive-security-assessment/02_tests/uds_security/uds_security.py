"""
==========================================================
Automotive White-Box Security Assessment
UDS Security Validation Tool

Author: Zukhra Abdulaeva

Description:
    Demonstration tool for validating selected UDS services
    during an Automotive White-Box Security Assessment.

Requirements:
    pip install python-can isotp
==========================================================
"""

import json
from datetime import datetime

import can


class UDSSecurityTester:

    def __init__(
        self,
        channel="can0",
        interface="socketcan",
        request_id=0x7E0,
        response_id=0x7E8
    ):

        self.bus = can.interface.Bus(
            channel=channel,
            interface=interface
        )

        self.request_id = request_id
        self.response_id = response_id

        self.results = []

    # -----------------------------------------------------

    def send_request(self, data):

        msg = can.Message(
            arbitration_id=self.request_id,
            data=data,
            is_extended_id=False
        )

        self.bus.send(msg)

        response = self.bus.recv(timeout=2)

        return response

    # -----------------------------------------------------

    def evaluate_response(self, response):

        if response is None:
            return "No Response"

        service = response.data[0]

        if service == 0x7F:

            return f"Negative Response (NRC 0x{response.data[2]:02X})"

        return "Positive Response"

    # -----------------------------------------------------

    def log_result(
        self,
        test_name,
        request,
        response,
        status
    ):

        if response:

            response_data = response.data.hex(" ")

        else:

            response_data = "None"

        self.results.append({

            "timestamp":
                datetime.now().isoformat(),

            "test":
                test_name,

            "request":
                " ".join(f"{b:02X}" for b in request),

            "response":
                response_data,

            "status":
                status

        })

    # -----------------------------------------------------

    def diagnostic_session_test(self):

        request = [0x10, 0x03]

        response = self.send_request(request)

        status = self.evaluate_response(response)

        self.log_result(
            "Diagnostic Session",
            request,
            response,
            status
        )

        print(f"[Session] {status}")

    # -----------------------------------------------------

    def security_access_test(self):

        request = [0x27, 0x01]

        response = self.send_request(request)

        status = self.evaluate_response(response)

        self.log_result(
            "Security Access",
            request,
            response,
            status
        )

        print(f"[Security Access] {status}")

    # -----------------------------------------------------

    def read_data_identifier_test(self):

        request = [0x22, 0xF1, 0x90]

        response = self.send_request(request)

        status = self.evaluate_response(response)

        self.log_result(
            "Read VIN",
            request,
            response,
            status
        )

        print(f"[ReadData] {status}")

    # -----------------------------------------------------

    def ecu_reset_test(self):

        request = [0x11, 0x01]

        response = self.send_request(request)

        status = self.evaluate_response(response)

        self.log_result(
            "ECU Reset",
            request,
            response,
            status
        )

        print(f"[ECU Reset] {status}")

    # -----------------------------------------------------

    def export_json(self, filename="uds_report.json"):

        with open(filename, "w") as f:

            json.dump(
                self.results,
                f,
                indent=4
            )

        print(f"[+] Report exported -> {filename}")

    # -----------------------------------------------------

    def print_summary(self):

        print("\n========== UDS TEST SUMMARY ==========")

        for result in self.results:

            print(
                f"{result['test']:<22}"
                f"{result['status']}"
            )

        print("======================================\n")


# ==========================================================

def main():

    tester = UDSSecurityTester()

    tester.diagnostic_session_test()

    tester.security_access_test()

    tester.read_data_identifier_test()

    tester.ecu_reset_test()

    tester.print_summary()

    tester.export_json()


if __name__ == "__main__":

    main()

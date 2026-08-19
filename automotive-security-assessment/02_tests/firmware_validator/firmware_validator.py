"""
==========================================================
Automotive White-Box Security Assessment
Firmware Integrity Validator

Author:
    Zukhra Abdulaeva

Description:
    Firmware Integrity Validator used during
    White-Box Automotive Security Assessments.

Features
--------
• SHA256 calculation
• Firmware metadata
• Integrity verification
• Firmware comparison
• JSON report generation

==========================================================
"""

import hashlib
import json
import os
from datetime import datetime


class FirmwareValidator:

    def __init__(self):

        self.results = []

    # -----------------------------------------------------

    def sha256(self, filename):

        sha = hashlib.sha256()

        with open(filename, "rb") as file:

            while True:

                chunk = file.read(4096)

                if not chunk:
                    break

                sha.update(chunk)

        return sha.hexdigest()

    # -----------------------------------------------------

    def firmware_information(self, filename):

        info = {

            "file":

                os.path.basename(filename),

            "size_bytes":

                os.path.getsize(filename),

            "modified":

                datetime.fromtimestamp(
                    os.path.getmtime(filename)
                ).isoformat(),

            "sha256":

                self.sha256(filename)

        }

        return info

    # -----------------------------------------------------

    def verify_integrity(self,
                         filename,
                         expected_hash):

        current = self.sha256(filename)

        passed = current.lower() == expected_hash.lower()

        result = {

            "timestamp":

                datetime.now().isoformat(),

            "test":

                "Firmware Integrity",

            "file":

                filename,

            "status":

                "PASS" if passed else "FAIL",

            "expected_hash":

                expected_hash,

            "calculated_hash":

                current

        }

        self.results.append(result)

        return result

    # -----------------------------------------------------

    def compare_firmware(self,
                         firmware_a,
                         firmware_b):

        hash_a = self.sha256(firmware_a)

        hash_b = self.sha256(firmware_b)

        identical = hash_a == hash_b

        result = {

            "timestamp":

                datetime.now().isoformat(),

            "test":

                "Firmware Comparison",

            "firmware_a":

                firmware_a,

            "firmware_b":

                firmware_b,

            "identical":

                identical,

            "hash_a":

                hash_a,

            "hash_b":

                hash_b

        }

        self.results.append(result)

        return result

    # -----------------------------------------------------

    def print_information(self, filename):

        info = self.firmware_information(filename)

        print("\n========== Firmware ==========\n")

        print(f"File      : {info['file']}")
        print(f"Size      : {info['size_bytes']} Bytes")
        print(f"Modified  : {info['modified']}")
        print(f"SHA256    :")
        print(info["sha256"])

        print("\n==============================\n")

    # -----------------------------------------------------

    def export_json(self,
                    filename="firmware_report.json"):

        report = {

            "generated":

                datetime.now().isoformat(),

            "assessment":

                "Firmware Integrity Validation",

            "results":

                self.results

        }

        with open(filename, "w") as file:

            json.dump(
                report,
                file,
                indent=4
            )

        print(f"[+] Report exported -> {filename}")


# ==========================================================

def main():

    validator = FirmwareValidator()

    firmware = "gateway_ecu.bin"

    validator.print_information(firmware)

    validator.verify_integrity(

        firmware,

        expected_hash="0123456789abcdef"

    )

    validator.compare_firmware(

        "gateway_ecu.bin",

        "gateway_ecu_v2.bin"

    )

    validator.export_json()


if __name__ == "__main__":

    main()

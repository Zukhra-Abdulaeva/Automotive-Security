"""
==========================================================
Automotive White-Box Security Assessment
Automotive Ethernet Scanner

Author: Zukhra Abdulaeva

Description:
    Inventory and security validation tool for Automotive
    Ethernet environments.

Requirements:
    pip install python-nmap

System requirement:
    nmap must be installed on the host.
==========================================================
"""

import ipaddress
import json
from datetime import datetime

import nmap


class AutomotiveEthernetScanner:

    def __init__(self, target):

        self.target = target
        self.scanner = nmap.PortScanner()
        self.results = []

    # -------------------------------------------------

    def validate_target(self):

        try:
            ipaddress.ip_network(self.target, strict=False)
            return True

        except ValueError:
            print("[!] Invalid target.")
            return False

    # -------------------------------------------------

    def scan(self,
             ports="22,80,443,13400,30490"):

        print(f"[+] Scanning {self.target}")

        self.scanner.scan(
            hosts=self.target,
            ports=ports,
            arguments="-Pn -sT"
        )

        for host in self.scanner.all_hosts():

            host_result = {

                "host": host,
                "state": self.scanner[host].state(),
                "services": []

            }

            for proto in self.scanner[host].all_protocols():

                for port in sorted(self.scanner[host][proto].keys()):

                    service = self.scanner[host][proto][port]

                    entry = {

                        "port": port,
                        "protocol": proto,
                        "state": service["state"],
                        "service": service["name"]

                    }

                    host_result["services"].append(entry)

            self.results.append(host_result)

    # -------------------------------------------------

    def analyze_services(self):

        print("\n========== Analysis ==========\n")

        for host in self.results:

            print(f"Host: {host['host']}")
            print(f"State: {host['state']}")

            for service in host["services"]:

                print(
                    f"  {service['port']:>5}/"
                    f"{service['protocol']:<4}"
                    f"{service['service']:<12}"
                    f"{service['state']}"
                )

                if service["port"] == 22:

                    print(
                        "      Recommendation: "
                        "Verify SSH authentication "
                        "and disable unused accounts."
                    )

                elif service["port"] == 80:

                    print(
                        "      Recommendation: "
                        "Use HTTPS where possible."
                    )

                elif service["port"] == 443:

                    print(
                        "      Recommendation: "
                        "Validate TLS configuration "
                        "and certificates."
                    )

                elif 30490 <= service["port"] <= 30509:

                    print(
                        "      Note: "
                        "Potential SOME/IP service."
                    )

            print()

    # -------------------------------------------------

    def export_json(self,
                    filename="ethernet_scan.json"):

        report = {

            "generated":

                datetime.now().isoformat(),

            "assessment":

                "Automotive Ethernet Security Validation",

            "results":

                self.results

        }

        with open(filename, "w") as f:

            json.dump(
                report,
                f,
                indent=4
            )

        print(f"[+] Report exported -> {filename}")

    # -------------------------------------------------

    def summary(self):

        hosts = len(self.results)

        services = sum(
            len(host["services"])
            for host in self.results
        )

        print("\n========== SUMMARY ==========")

        print(f"Hosts discovered : {hosts}")
        print(f"Services detected: {services}")

        print("=============================\n")


# ======================================================

def main():

    scanner = AutomotiveEthernetScanner(
        "192.168.10.0/24"
    )

    if not scanner.validate_target():
        return

    scanner.scan()

    scanner.analyze_services()

    scanner.summary()

    scanner.export_json()


if __name__ == "__main__":

    main()

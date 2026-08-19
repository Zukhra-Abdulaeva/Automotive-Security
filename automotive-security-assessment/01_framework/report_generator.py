"""
==========================================================
Automotive White-Box Security Assessment
Security Report Generator

Author:
    Zukhra Abdulaeva

Description:
    Consolidates security assessment results from multiple
    test modules into a single report.

Supported Inputs
----------------
• CAN Sniffer
• UDS Security Tester
• Ethernet Scanner
• Firmware Validator

Supported Outputs
-----------------
• JSON
• Markdown
• HTML

==========================================================
"""

import json
from datetime import datetime
from pathlib import Path


class ReportGenerator:

    def __init__(self):

        self.findings = []

    # -------------------------------------------------

    def load_json(self, filename):

        path = Path(filename)

        if not path.exists():

            print(f"[!] File not found: {filename}")
            return

        with open(path, "r") as file:

            data = json.load(file)

        self.findings.append({

            "source": path.stem,

            "data": data

        })

        print(f"[+] Loaded {filename}")

    # -------------------------------------------------

    def summary(self):

        print("\n========== Assessment Summary ==========\n")

        print(f"Modules analysed : {len(self.findings)}")

        for module in self.findings:

            print(f" • {module['source']}")

        print("\n========================================\n")

    # -------------------------------------------------

    def export_json(self,
                    filename="security_assessment.json"):

        report = {

            "generated":

                datetime.now().isoformat(),

            "assessment":

                "Automotive White-Box Security Assessment",

            "modules":

                self.findings

        }

        with open(filename, "w") as file:

            json.dump(
                report,
                file,
                indent=4
            )

        print(f"[+] JSON report -> {filename}")

    # -------------------------------------------------

    def export_markdown(self,
                        filename="Security_Report.md"):

        with open(filename, "w") as file:

            file.write("# Automotive White-Box Security Assessment\n\n")

            file.write(
                f"Generated: "
                f"{datetime.now().isoformat()}\n\n"
            )

            for module in self.findings:

                file.write(
                    f"## {module['source']}\n\n"
                )

                file.write("```json\n")

                file.write(
                    json.dumps(
                        module["data"],
                        indent=4
                    )
                )

                file.write("\n```\n\n")

        print(f"[+] Markdown report -> {filename}")

    # -------------------------------------------------

    def export_html(self,
                    filename="Security_Report.html"):

        html = f"""
<html>

<head>

<title>
Automotive Security Assessment
</title>

<style>

body {{

font-family: Arial;
margin:40px;

}}

table {{

border-collapse: collapse;
width:100%;

}}

th,td {{

border:1px solid #cccccc;
padding:8px;

}}

th {{

background:#efefef;

}}

</style>

</head>

<body>

<h1>
Automotive White-Box Security Assessment
</h1>

<p>
Generated:
{datetime.now().isoformat()}
</p>

"""

        for module in self.findings:

            html += f"<h2>{module['source']}</h2>"

            html += "<pre>"

            html += json.dumps(
                module["data"],
                indent=4
            )

            html += "</pre>"

        html += """

</body>

</html>

"""

        with open(filename, "w") as file:

            file.write(html)

        print(f"[+] HTML report -> {filename}")


# =======================================================

def main():

    report = ReportGenerator()

    report.load_json("can_capture.json")

    report.load_json("uds_report.json")

    report.load_json("ethernet_scan.json")

    report.load_json("firmware_report.json")

    report.summary()

    report.export_json()

    report.export_markdown()

    report.export_html()


if __name__ == "__main__":

    main()

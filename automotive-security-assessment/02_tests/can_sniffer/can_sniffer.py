"""
==========================================================
Automotive White-Box Security Assessment
CAN Traffic Sniffer
Author: Zukhra Abdulaeva

Description:
    Reads CAN messages via SocketCAN, optionally filters
    specific CAN IDs, stores captured traffic and exports
    the results to CSV.

Requirements:
    pip install python-can
==========================================================
"""

import csv
from datetime import datetime
from collections import Counter

import can


class CANSniffer:
    """
    Simple CAN traffic analyzer for SocketCAN interfaces.
    """

    def __init__(self, channel="can0", interface="socketcan"):
        self.channel = channel
        self.interface = interface
        self.bus = None
        self.messages = []

    def connect(self):
        """
        Connect to SocketCAN interface.
        """
        self.bus = can.interface.Bus(
            channel=self.channel,
            interface=self.interface
        )

        print(f"[+] Connected to {self.channel}")

    def receive_messages(self,
                         duration=10,
                         filter_ids=None):
        """
        Capture CAN traffic.

        duration:
            Capture time in seconds.

        filter_ids:
            Optional list of arbitration IDs.
        """

        print(f"[+] Capturing CAN traffic ({duration}s)...")

        start = datetime.now()

        while (datetime.now() - start).seconds < duration:

            msg = self.bus.recv(timeout=1)

            if msg is None:
                continue

            if filter_ids and msg.arbitration_id not in filter_ids:
                continue

            self.save_message(msg)

            print(
                f"ID: 0x{msg.arbitration_id:03X} "
                f"DATA: {msg.data.hex(' ')}"
            )

    def save_message(self, msg):
        """
        Store received message.
        """

        self.messages.append({
            "timestamp": datetime.now().isoformat(),
            "id": hex(msg.arbitration_id),
            "dlc": msg.dlc,
            "data": msg.data.hex(" ")
        })

    def export_csv(self,
                   filename="can_capture.csv"):
        """
        Export captured messages.
        """

        with open(filename,
                  "w",
                  newline="") as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=[
                    "timestamp",
                    "id",
                    "dlc",
                    "data"
                ]
            )

            writer.writeheader()

            writer.writerows(self.messages)

        print(f"[+] CSV exported -> {filename}")

    def statistics(self):
        """
        Print simple traffic statistics.
        """

        ids = [msg["id"] for msg in self.messages]

        counter = Counter(ids)

        print("\n========== Statistics ==========")

        print(f"Messages: {len(self.messages)}")
        print(f"Unique IDs: {len(counter)}")

        print("\nTop CAN IDs:")

        for can_id, count in counter.most_common(10):
            print(f"{can_id:<8} {count}")

        print("===============================\n")

def main():

    sniffer = CANSniffer(
        channel="can0"
    )

    sniffer.connect()

    sniffer.receive_messages(
        duration=20,

        # Example filter
        filter_ids=[
            0x100,
            0x200,
            0x321
        ]
    )

    sniffer.statistics()

    sniffer.export_csv()


if __name__ == "__main__":
    main()

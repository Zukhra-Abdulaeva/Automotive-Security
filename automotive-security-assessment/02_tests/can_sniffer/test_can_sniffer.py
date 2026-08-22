from unittest.mock import MagicMock
import can
from can_sniffer.can_sniffer import CANSniffer

def test_save_message():
    sniffer = CANSniffer()
    msg = can.Message(arbitration_id=0x100, data=b"\x01\x02\x03\x04", dlc=4)

    sniffer.save_message(msg)

    assert sniffer.messages[0]["id"] == "0x100"
    assert sniffer.messages[0]["data"] == "01 02 03 04"
    
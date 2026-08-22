import time
import can

bus = can.interface.Bus(channel="vcan0", interface="virtual")

messages = [
    can.Message(arbitration_id=0x100, data=b"\x01\x00\xFF\xA2\x12\x44\x55\x66", dlc=8),
    can.Message(arbitration_id=0x321, data=b"\x11\x22\x33\x44\x55\x66\x77\x88", dlc=8),
    can.Message(arbitration_id=0x200, data=b"\xFF"*8, dlc=8),
]

print("[+] Sending fake CAN messages...")

start = time.time()
while time.time() - start < 5:
    for msg in messages:
        bus.send(msg)
        print(f"Sent ID: 0x{msg.arbitration_id:03X}")
        time.sleep(0.5)

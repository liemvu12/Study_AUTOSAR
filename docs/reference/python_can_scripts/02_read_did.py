"""
Read Data By Identifier (Service 0x22)
Äá»c DID 0xF190 (VIN) vÃ  0xF18C (ECU Serial Number)
"""
import can

TX_ID = 0x7E0  # Physical addressing
RX_ID = 0x7E8

def read_did(bus, did: int):
    # Service 0x22, sau Ä‘Ã³ lÃ  2 byte cá»§a DID
    data = [0x22, (did >> 8) & 0xFF, did & 0xFF]
    msg = can.Message(arbitration_id=TX_ID, data=data, is_extended_id=False)
    bus.send(msg)
    print(f"Request DID 0x{did:04X}: {' '.join(f'{b:02X}' for b in data)}")

    response = bus.recv(timeout=1.0)
    if response and response.arbitration_id == RX_ID:
        if response.data[0] == 0x62: # Positive response (0x22 + 0x40)
            did_recv = (response.data[1] << 8) | response.data[2]
            value = response.data[3:]
            print(f"RX Success DID 0x{did_recv:04X}: {bytes(value).decode('ascii', errors='ignore')}")
        elif response.data[0] == 0x7F: # NRC
            print(f"NRC Error: 0x{response.data[2]:02X}")
    else:
        print("Timeout khi chá» ECU tráº£ lá»i.")

if __name__ == '__main__':
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    try:
        read_did(bus, 0xF190) # VIN
        read_did(bus, 0xF18C) # Serial Number
    finally:
        bus.shutdown()

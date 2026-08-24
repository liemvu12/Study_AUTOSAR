"""
Clear Diagnostic Information (Service 0x14)
XoÃ¡ mÃ£ lá»—i.
"""
import can

TX_ID = 0x7E0
RX_ID = 0x7E8

def clear_dtc(bus):
    # Clear all DTCs: 14 FF FF FF
    req = [0x14, 0xFF, 0xFF, 0xFF]
    bus.send(can.Message(arbitration_id=TX_ID, data=req, is_extended_id=False))
    print(f"Gá»­i Request Clear DTC: {' '.join(f'{b:02X}' for b in req)}")
    
    res = bus.recv(timeout=1.0)
    if res and res.arbitration_id == RX_ID:
        if res.data[0] == 0x54:
            print("XÃ³a DTC THÃ€NH CÃ”NG.")
        elif res.data[0] == 0x7F:
            print(f"XÃ³a DTC THáº¤T Báº I. NRC: 0x{res.data[2]:02X}")
    else:
        print("Timeout.")

if __name__ == '__main__':
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    try:
        clear_dtc(bus)
    finally:
        bus.shutdown()

"""
Read DTC Information (Service 0x19)
Äá»c danh sÃ¡ch cÃ¡c mÃ£ lá»—i.
"""
import can

TX_ID = 0x7E0
RX_ID = 0x7E8

def parse_dtc_status(status_byte):
    statuses = []
    if status_byte & 0x01: statuses.append("TestFailed")
    if status_byte & 0x08: statuses.append("ConfirmedDTC")
    if status_byte & 0x40: statuses.append("TestNotCompletedThisOperationCycle")
    if status_byte & 0x80: statuses.append("WarningIndicatorRequested")
    return ", ".join(statuses) if statuses else "None"

def read_dtc(bus):
    # 19 02 [mask]: Read DTCs with status byte (mask 0xFF Ä‘á»ƒ Ä‘á»c háº¿t)
    req = [0x19, 0x02, 0xFF]
    bus.send(can.Message(arbitration_id=TX_ID, data=req, is_extended_id=False))
    print(f"Gá»­i Request Read DTC: {' '.join(f'{b:02X}' for b in req)}")
    
    # Thá»±c táº¿ vá»›i UDS, response cÃ³ thá»ƒ lÃ  ISO-TP Ä‘a khung (multi-frame).
    # á»ž Ä‘Ã¢y code mÃ´ phá»ng 1 single frame response Ä‘Æ¡n giáº£n Ä‘á»ƒ minh há»a.
    res = bus.recv(timeout=1.0)
    if res and res.arbitration_id == RX_ID:
        if res.data[0] == 0x59 and res.data[1] == 0x02:
            print("Äá»c DTC thÃ nh cÃ´ng. Danh sÃ¡ch:")
            # Byte 2 lÃ  status availability mask
            dtc_data = res.data[3:]
            # Má»—i DTC gá»“m 4 bytes: 3 bytes DTC ID + 1 byte status
            for i in range(0, len(dtc_data), 4):
                if i + 3 < len(dtc_data):
                    dtc_id = (dtc_data[i] << 16) | (dtc_data[i+1] << 8) | dtc_data[i+2]
                    status = dtc_data[i+3]
                    status_desc = parse_dtc_status(status)
                    print(f" - DTC: 0x{dtc_id:06X}, Status: 0x{status:02X} ({status_desc})")
        elif res.data[0] == 0x7F:
            print(f"Lá»—i Read DTC. NRC: 0x{res.data[2]:02X}")
    else:
        print("Timeout.")

if __name__ == '__main__':
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    try:
        read_dtc(bus)
    finally:
        bus.shutdown()
